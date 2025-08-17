from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, Literal

from dotenv import load_dotenv
from google import genai
from google.genai import types

from config import settings
from model import TEFTaskAResponse, TEFTaskBResponse, TEFJudgeResponse
from prompt_taskA import (
    eval1_system_instruction_taskA, eval1_taskA_prompt,
    eval2_system_instruction_taskA, eval2_taskA_prompt,
    judge_system_instruction_taskA, judge_prompt_taskA,
)
from prompt_taskB import (
    eval1_system_instruction_taskB, eval1_taskB_prompt,
    eval2_system_instruction_taskB, eval2_taskB_prompt,
    judge_system_instruction_taskB, judge_prompt_taskB,
)

import copy
import json
import re
import pandas as pd

load_dotenv()

app = FastAPI(title=settings.app_name, version=settings.app_version)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini client and model names (relying on GOOGLE_API_KEY in env)
client = genai.Client()
model_pro = settings.ai_model_pro
model_flash = settings.ai_model_fast


# Utilities copied from test_script.py to ensure identical schema behavior
from pydantic import BaseModel as _BaseModel

def fully_flatten_pydantic_schema(model: type[_BaseModel], nested_title: str = "CategoryFeedback") -> dict:
    raw_schema = model.model_json_schema()
    defs = raw_schema.get("$defs", {})

    def _resolve_refs(schema: dict) -> dict:
        schema = copy.deepcopy(schema)
        if isinstance(schema, dict):
            if "$ref" in schema:
                ref_path = schema.pop("$ref")
                ref_name = ref_path.split("/")[-1]
                ref_schema = defs.get(ref_name, {})
                schema.update(_resolve_refs(ref_schema))
            if "allOf" in schema:
                merged = {}
                for subschema in schema.pop("allOf"):
                    merged.update(_resolve_refs(subschema))
                schema.update(merged)
            for k, v in schema.items():
                schema[k] = _resolve_refs(v)
            if schema.get("type") == "object" and "properties" in schema:
                if set(["rating","justification","original","correction","recommendation"]).issubset(schema["properties"].keys()):
                    schema["title"] = nested_title
        elif isinstance(schema, list):
            schema = [_resolve_refs(item) for item in schema]
        return schema

    flat_schema = _resolve_refs(raw_schema)
    flat_schema.pop("$defs", None)
    return flat_schema


def flatten_pydantic_schema(model: type[_BaseModel]) -> dict:
    raw_schema = model.model_json_schema()
    defs = raw_schema.get("$defs", {})

    def resolve(schema):
        if isinstance(schema, dict):
            schema = copy.deepcopy(schema)
            if "$ref" in schema:
                ref_name = schema["$ref"].split("/")[-1]
                return resolve(defs.get(ref_name, {}))
            if "allOf" in schema:
                merged = {}
                for subschema in schema.pop("allOf"):
                    merged.update(resolve(subschema))
                schema.update(merged)
            if "prefixItems" in schema:
                schema["items"] = schema.pop("prefixItems")
            for k, v in list(schema.items()):
                schema[k] = resolve(v)
            for key in ["$defs", "$ref", "allOf"]:
                schema.pop(key, None)
            return schema
        elif isinstance(schema, list):
            return [resolve(item) for item in schema]
        else:
            return schema

    flat = resolve(raw_schema)
    flat.pop("$defs", None)
    return flat


def extract_feedback_df(response, metrics):
    match = re.search(r'\{.*\}', response.text, re.DOTALL)
    if not match:
        raise ValueError('No JSON object found in response.text')
    response_json_str = match.group(0)
    response_json = json.loads(response_json_str)
    import pandas as _pd
    results = {}
    for metric in metrics:
        data = response_json.get(metric, {})
        results[metric] = {
            'rating': data.get('rating'),
            'justification': data.get('justification'),
            'original': data.get('original', []),
            'correction': data.get('correction', []),
            'recommendation': data.get('recommendation'),
        }
    df = _pd.DataFrame.from_dict(results, orient='index')
    df.index.name = 'metric'
    df.reset_index(inplace=True)
    return df


def extract_feedback_summary(df1, df2):
    rating = float(round((df1.rating.mean()*0.5 + df2.rating.mean()*0.5)/5*100,2))
    justification = ' '.join(df1.justification.tolist()) + ' '.join(df2.justification.tolist())
    recommendation = ' '.join(df1.recommendation.tolist()) + ' '.join(df2.recommendation.tolist())
    originals = [item for sublist in df1.original.tolist() + df2.original.tolist() if sublist for item in sublist]
    corrections = [item for sublist in df1.correction.tolist() + df2.correction.tolist() if sublist for item in sublist]
    return rating, justification, recommendation, originals, corrections


# Schemas
output_schema_taskA = fully_flatten_pydantic_schema(TEFTaskAResponse)
output_schema_taskB = fully_flatten_pydantic_schema(TEFTaskBResponse)
judge_output_schema = flatten_pydantic_schema(TEFJudgeResponse)

# Metrics
metrics_taskA = ['task_fulfillment', 'organization_coherence', 'content_relevance', 'vocabulary', 'grammar_syntax', 'cohesion', 'style_adaptability']
metrics_taskB = ['task_fulfillment', 'structure', 'argumentation', 'vocabulary', 'grammar_syntax', 'cohesion', 'tone', 'style_adaptability']


class GenerateQuestionRequest(BaseModel):
    task: Literal['A','B']

class EvaluateTaskARequest(BaseModel):
    task_a_question: str
    task_a_response: str

class EvaluateTaskBRequest(BaseModel):
    task_b_question: str
    task_b_response: str


@app.get("/", response_class=HTMLResponse)
async def root():
    with open("index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/api/config")
async def get_config():
    return {
        "appName": settings.app_name,
        "version": settings.app_version,
        "writingTimeMinutes": settings.writing_time_minutes,
        "minWordsTaskA": settings.min_words_task_a,
        "minWordsTaskB": settings.min_words_task_b,
    }


@app.post("/api/question")
async def generate_question(payload: GenerateQuestionRequest):
    # Simple built-in prompts for MVP
    if payload.task == 'A':
        question = (
            "Type de document : le début d’un article de presse (rubrique faits-divers)\n"
            "Objectif : écrire la suite de l’article (80 mots minimum)\n"
            "Voici le début d’un article de presse. Terminez cet article : en ajoutant à la suite un texte de 80 mots minimum ; en faisant plusieurs paragraphes.\n"
            "Un chien perdu dans le parc..."
        )
    else:
        question = (
            "Type de document : une phrase extraite d’un journal\n"
            "Objectif : exprimer son point de vue et le justifier (200 mots minimum)\n"
            "\"Les examens scolaires ne mesurent pas vraiment l’intelligence.\"\n"
            "Écrivez une lettre au journal pour défendre votre point de vue."
        )
    return {"question": question}


@app.post("/api/evaluate/task-a")
async def evaluate_task_a(payload: EvaluateTaskARequest):
    # Build Task A eval prompts
    word_count_taskA = len(payload.task_a_response.split())
    taskA_content_eval1 = eval1_taskA_prompt.format(
        question=payload.task_a_question,
        response=payload.task_a_response,
        word_count=word_count_taskA,
    )
    taskA_content_eval2 = eval2_taskA_prompt.format(
        question=payload.task_a_question,
        response=payload.task_a_response,
        word_count=word_count_taskA,
    )

    # Call Gemini for Task A
    resp_eval1_A = client.models.generate_content(
        model=model_pro,
        config=types.GenerateContentConfig(
            system_instruction=eval1_system_instruction_taskA,
            response_mime_type='application/json',
            response_schema=output_schema_taskA,
        ),
        contents=taskA_content_eval1,
    )
    resp_eval2_A = client.models.generate_content(
        model=model_pro,
        config=types.GenerateContentConfig(
            system_instruction=eval2_system_instruction_taskA,
            response_mime_type='application/json',
            response_schema=output_schema_taskA,
        ),
        contents=taskA_content_eval2,
    )

    # Parse Task A
    df1A = extract_feedback_df(resp_eval1_A, metrics_taskA)
    df2A = extract_feedback_df(resp_eval2_A, metrics_taskA)
    rating_A, justification_A, recommendation_A, originals_A, corrections_A = extract_feedback_summary(df1A, df2A)

    # Judge for Task A
    taskA_judge_content = judge_prompt_taskA.format(
        justification=justification_A,
        recommendations=recommendation_A,
        originals=originals_A,
        corrections=corrections_A,
    )
    resp_judge_A = client.models.generate_content(
        model=model_pro,
        config=types.GenerateContentConfig(
            system_instruction=judge_system_instruction_taskA,
            response_mime_type='application/json',
            response_schema=flatten_pydantic_schema(TEFJudgeResponse),
        ),
        contents=taskA_judge_content,
    )

    return {
        "eval1": json.loads(re.search(r"\{.*\}", resp_eval1_A.text, re.DOTALL).group(0)),
        "eval2": json.loads(re.search(r"\{.*\}", resp_eval2_A.text, re.DOTALL).group(0)),
        "judge": json.loads(re.search(r"\{.*\}", resp_judge_A.text, re.DOTALL).group(0)),
        "rating": rating_A,
    }


@app.post("/api/evaluate/task-b")
async def evaluate_task_b(payload: EvaluateTaskBRequest):
    # Build Task B eval prompts
    word_count_taskB = len(payload.task_b_response.split())
    taskB_content_eval1 = eval1_taskB_prompt.format(
        question=payload.task_b_question,
        response=payload.task_b_response,
        word_count=word_count_taskB,
    )
    taskB_content_eval2 = eval2_taskB_prompt.format(
        question=payload.task_b_question,
        response=payload.task_b_response,
        word_count=word_count_taskB,
    )
    resp_eval1_B = client.models.generate_content(
        model=model_pro,
        config=types.GenerateContentConfig(
            system_instruction=eval1_system_instruction_taskB,
            response_mime_type='application/json',
            response_schema=output_schema_taskB,
        ),
        contents=taskB_content_eval1,
    )
    resp_eval2_B = client.models.generate_content(
        model=model_pro,
        config=types.GenerateContentConfig(
            system_instruction=eval2_system_instruction_taskB,
            response_mime_type='application/json',
            response_schema=output_schema_taskB,
        ),
        contents=taskB_content_eval2,
    )
    df1B = extract_feedback_df(resp_eval1_B, metrics_taskB)
    df2B = extract_feedback_df(resp_eval2_B, metrics_taskB)
    rating_B, justification_B, recommendation_B, originals_B, corrections_B = extract_feedback_summary(df1B, df2B)
    taskB_judge_content = judge_prompt_taskB.format(
        justification=justification_B,
        recommendations=recommendation_B,
        originals=originals_B,
        corrections=corrections_B,
    )
    resp_judge_B = client.models.generate_content(
        model=model_pro,
        config=types.GenerateContentConfig(
            system_instruction=judge_system_instruction_taskB,
            response_mime_type='application/json',
            response_schema=flatten_pydantic_schema(TEFJudgeResponse),
        ),
        contents=taskB_judge_content,
    )
    return {
        "eval1": json.loads(re.search(r"\{.*\}", resp_eval1_B.text, re.DOTALL).group(0)),
        "eval2": json.loads(re.search(r"\{.*\}", resp_eval2_B.text, re.DOTALL).group(0)),
        "judge": json.loads(re.search(r"\{.*\}", resp_judge_B.text, re.DOTALL).group(0)),
        "rating": rating_B,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)
