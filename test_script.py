
# Import Gemini API and types
from google import genai
from google.genai import types


# Import model schemas and prompt templates for both Task A and Task B
from model import TEFTaskAResponse, TEFTaskBResponse, TEFJudgeResponse
from prompt_taskA import eval1_system_instruction_taskA, eval1_taskA_prompt
from prompt_taskA import eval2_system_instruction_taskA, eval2_taskA_prompt
from prompt_taskA import judge_system_instruction_taskA, judge_prompt_taskA
from prompt_taskB import eval1_system_instruction_taskB, eval1_taskB_prompt
from prompt_taskB import eval2_system_instruction_taskB, eval2_taskB_prompt
from prompt_taskB import judge_system_instruction_taskB, judge_prompt_taskB
# Import sample questions and responses for both tasks
from test_sample import task_a_question, task_a_response, task_b_question, task_b_response


# Standard library and third-party imports
import pandas as pd
import copy
import json
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError
import re


# Load environment variables from .env file
load_dotenv()


# Utility to fully flatten a Pydantic v2 JSON schema, resolving $ref and allOf
def fully_flatten_pydantic_schema(model: type[BaseModel], nested_title: str = "CategoryFeedback") -> dict:
    """
    Flattens a Pydantic model schema by resolving $ref and allOf, and sets a custom title for nested objects.
    """
    raw_schema = model.model_json_schema()
    defs = raw_schema.get("$defs", {})
    def _resolve_refs(schema: dict) -> dict:
        schema = copy.deepcopy(schema)
        if isinstance(schema, dict):
            # Resolve $ref
            if "$ref" in schema:
                ref_path = schema.pop("$ref")
                ref_name = ref_path.split("/")[-1]
                ref_schema = defs.get(ref_name, {})
                schema.update(_resolve_refs(ref_schema))
            # Flatten allOf
            if "allOf" in schema:
                merged = {}
                for subschema in schema.pop("allOf"):
                    merged.update(_resolve_refs(subschema))
                schema.update(merged)
            # Recurse into nested dicts
            for k, v in schema.items():
                schema[k] = _resolve_refs(v)
            # Set nested title for feedback objects
            if schema.get("type") == "object" and "properties" in schema:
                if set(["rating","justification","original","correction","recommendation"]).issubset(schema["properties"].keys()):
                    schema["title"] = nested_title
        elif isinstance(schema, list):
            schema = [_resolve_refs(item) for item in schema]
        return schema
    flat_schema = _resolve_refs(raw_schema)
    flat_schema.pop("$defs", None)
    return flat_schema


# Utility to flatten a Pydantic schema (for judge output)
def flatten_pydantic_schema(model: type[BaseModel]) -> dict:
    """
    Flattens a Pydantic model schema by resolving $ref, allOf, and prefixItems.
    """
    raw_schema = model.model_json_schema()
    defs = raw_schema.get("$defs", {})
    def resolve(schema):
        if isinstance(schema, dict):
            schema = copy.deepcopy(schema)
            # Resolve $ref
            if "$ref" in schema:
                ref_name = schema["$ref"].split("/")[-1]
                return resolve(defs.get(ref_name, {}))
            # Merge allOf
            if "allOf" in schema:
                merged = {}
                for subschema in schema.pop("allOf"):
                    merged.update(resolve(subschema))
                schema.update(merged)
            # Convert prefixItems → items
            if "prefixItems" in schema:
                schema["items"] = schema.pop("prefixItems")
            # Recursively process dict
            for k, v in list(schema.items()):
                schema[k] = resolve(v)
            # Remove unwanted keys
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


# Extracts feedback for each metric from the model response and returns a DataFrame
def extract_feedback_df(response, metrics):
    """
    Extracts rating, justification, original, correction, and recommendation for each metric.
    Returns a DataFrame with the extracted info.
    """
    match = re.search(r'\{.*\}', response.text, re.DOTALL)
    if not match:
        raise ValueError('No JSON object found in response.text')
    response_json_str = match.group(0)
    response_json = json.loads(response_json_str)
    results = {}
    for metric in metrics:
        data = response_json.get(metric, {})
        rating = data.get('rating')
        justification = data.get('justification')
        recommendation = data.get('recommendation')
        originals = data.get('original', [])
        corrections = data.get('correction', [])
        results[metric] = {
            'rating': rating,
            'justification': justification,
            'original': originals,
            'correction': corrections,
            'recommendation': recommendation
        }
    df = pd.DataFrame.from_dict(results, orient='index')
    df.index.name = 'metric'
    df.reset_index(inplace=True)
    return df


# Summarizes feedback from two DataFrames, flattening originals/corrections
def extract_feedback_summary(df1, df2):
    """
    Combines feedback from two DataFrames, flattens originals/corrections, and computes mean rating.
    """
    rating = float(round((df1.rating.mean()*0.5 + df2.rating.mean()*0.5)/5*100,2))
    justification = ' '.join(df1.justification.tolist()) + ' '.join(df2.justification.tolist())
    recommendation = ' '.join(df1.recommendation.tolist()) + ' '.join(df2.recommendation.tolist())
    # Flatten all originals and corrections to single lists
    originals = [item for sublist in df1.original.tolist() + df2.original.tolist() if sublist for item in sublist]
    corrections = [item for sublist in df1.correction.tolist() + df2.correction.tolist() if sublist for item in sublist]
    return rating, justification, recommendation, originals, corrections


# Generic Gemini API call function for model content generation
def generate_gemini_response(system_instruction, response_schema, contents, model='gemini-2.5-flash'):
    """
    Calls the Gemini model with the given system instruction, schema, and contents.
    """
    return client.models.generate_content(
        model=model,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type='application/json',
            response_schema=response_schema
        ),
        contents=contents
    )


# Prepare output schemas for both tasks and judge
output_schema_taskA = fully_flatten_pydantic_schema(TEFTaskAResponse)
output_schema_taskB = fully_flatten_pydantic_schema(TEFTaskBResponse)
judge_output_schema = flatten_pydantic_schema(TEFJudgeResponse)

# Calculate word counts for responses
word_count_taskA = len(task_a_response.split())
word_count_taskB = len(task_b_response.split())

# Initialize Gemini client and model names
client = genai.Client()
model_pro = 'gemini-2.5-pro'
model_flash = 'gemini-2.5-flash'

# Format prompts for both evaluators for Task A
taskA_content_eval1 = eval1_taskA_prompt.format(
    question=task_a_question,
    response=task_a_response,
    word_count=word_count_taskA
)
taskA_content_eval2 = eval2_taskA_prompt.format(
    question=task_a_question,
    response=task_a_response,
    word_count=word_count_taskA   
)
# Format prompts for both evaluators for Task B
taskB_content_eval1 = eval1_taskB_prompt.format(
    question=task_b_question,
    response=task_b_response,
    word_count=word_count_taskB
)
taskB_content_eval2 = eval2_taskB_prompt.format(
    question=task_b_question,
    response=task_b_response,
    word_count=word_count_taskB
)


# Get model responses for both evaluators for Task A
response_eval1_taskA = generate_gemini_response(
    system_instruction=taskA_content_eval1,
    response_schema=output_schema_taskA,
    contents=taskA_content_eval1
)
response_eval2_taskA = generate_gemini_response(
    system_instruction=taskA_content_eval2,
    response_schema=output_schema_taskA,
    contents=taskA_content_eval2
)
# Get model responses for both evaluators for Task B
response_eval1_taskB = generate_gemini_response(
    system_instruction=taskB_content_eval1,
    response_schema=output_schema_taskB,
    contents=taskB_content_eval1
)
response_eval2_taskB = generate_gemini_response(
    system_instruction=taskB_content_eval2,
    response_schema=output_schema_taskB,
    contents=taskB_content_eval2
)


# Define metrics for each task
metrics_taskA = ['task_fulfillment', 'organization_coherence', 'content_relevance', 'vocabulary', 'grammar_syntax', 'cohesion', 'style_adaptability']
metrics_taskB = ['task_fulfillment', 'structure', 'argumentation', 'vocabulary', 'grammar_syntax', 'cohesion', 'tone', 'style_adaptability']

# Extract feedback DataFrames and summaries for Task A
df_1_taskA = extract_feedback_df(response_eval1_taskA, metrics_taskA)
df_2_taskA = extract_feedback_df(response_eval2_taskA, metrics_taskA)
rating_taskA, justification_taskA, recommendations_taskA, originals_taskA, corrections_taskA = extract_feedback_summary(df_1_taskA, df_2_taskA)

# Extract feedback DataFrames and summaries for Task B
df_1_taskB = extract_feedback_df(response_eval1_taskB, metrics_taskB)
df_2_taskB = extract_feedback_df(response_eval2_taskB, metrics_taskB)
rating_taskB, justification_taskB, recommendations_taskB, originals_taskB, corrections_taskB = extract_feedback_summary(df_1_taskB, df_2_taskB)

# Format judge prompts for both tasks
taskA_judge_content = judge_prompt_taskA.format(
    justification = justification_taskA,
    recommendations = recommendations_taskA,
    originals = originals_taskA,
    corrections = corrections_taskA)
taskB_judge_content = judge_prompt_taskB.format(
    justification = justification_taskB,
    recommendations = recommendations_taskB,
    originals = originals_taskB,
    corrections = corrections_taskB)

# Get judge model responses for both tasks
response_judge_taskA = client.models.generate_content(
    model=model_pro,
    config=types.GenerateContentConfig(
        system_instruction=judge_system_instruction_taskA,
        response_mime_type='application/json',
        response_schema=judge_output_schema),
    contents=taskA_judge_content
)
response_judge_taskB = client.models.generate_content(
    model=model_pro,
    config=types.GenerateContentConfig(
        system_instruction=judge_system_instruction_taskB,
        response_mime_type='application/json',
        response_schema=judge_output_schema),
    contents=taskB_judge_content
)
