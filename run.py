import copy
import json
import re
import warnings
# Suppress all UserWarnings globally (including Pydantic field shadowing)
warnings.simplefilter("ignore", UserWarning)
from datetime import datetime, timedelta

import pandas as _pd
import uvicorn, webbrowser
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Literal, Optional

from google import genai
from google.genai import types
import os

from config import settings
from model import (
    TEFJudgeResponse,
    TEFTaskAResponse,
    TEFTaskBResponse,
    User,
    Submission,
    Base,
    engine,
    SessionLocal,
    get_db,
)
from prompt_taskA import (
    eval1_system_instruction_taskA,
    eval1_taskA_prompt,
    eval2_system_instruction_taskA,
    eval2_taskA_prompt,
    judge_prompt_taskA,
    judge_system_instruction_taskA,
)
from prompt_taskB import (
    eval1_system_instruction_taskB,
    eval1_taskB_prompt,
    eval2_system_instruction_taskB,
    eval2_taskB_prompt,
    judge_prompt_taskB,
    judge_system_instruction_taskB,
)

load_dotenv()

app = FastAPI(title=settings.app_name, version=settings.app_version)

# Mount static files (CSS and JS)
app.mount("/static", StaticFiles(directory="."), name="static")

# Serve individual static files at root level
@app.get("/styles.css")
async def get_styles():
    return FileResponse("styles.css", media_type="text/css")

@app.get("/scripts.js")
async def get_scripts():
    return FileResponse("scripts.js", media_type="application/javascript")

# Serve favicon.ico to prevent 404 errors
@app.get("/favicon.ico")
async def favicon():
    return FileResponse("favicon.ico")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================
# Auth & Database Setup
# =====================

# DB now imported from model.py


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


# JWT
ALGORITHM = settings.jwt_algorithm
SECRET_KEY = os.getenv("SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCredentials(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str


def get_current_user(token: Optional[str] = None, request: Request = None, db: Session = Depends(get_db)) -> User:
    # Support Authorization: Bearer <token>
    if token is None and request is not None:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header.split(" ", 1)[1].strip()
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.get(User, int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


@app.on_event("startup")
def on_startup():
    # Create tables
    Base.metadata.create_all(bind=engine)
    # Ensure test user exists
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == "testing").first()
        if not user:
            db.add(User(username="testing", hashed_password=get_password_hash("testing")))
            db.commit()
    finally:
        db.close()


# =====================
# Gemini client
# =====================
client = genai.Client()
model_pro = settings.ai_model_pro
model_flash = settings.ai_model_fast


# =====================
# Utilities for schemas
# =====================
from pydantic import BaseModel as _BaseModel

def fully_flatten_pydantic_schema(model: type[BaseModel], nested_title: str = "CategoryFeedback") -> dict:
    """
    Fully flatten Pydantic v2 JSON schema:
    - Replaces $ref with the definition from $defs
    - Removes $defs and allOf
    - Sets nested_title for nested objects
    """
    raw_schema = model.model_json_schema()

    # Grab definitions
    defs = raw_schema.get("$defs", {})

    def _resolve_refs(schema: dict) -> dict:
        schema = copy.deepcopy(schema)
        if isinstance(schema, dict):
            # Resolve $ref
            if "$ref" in schema:
                ref_path = schema.pop("$ref")
                # In Pydantic v2, refs are like "#/$defs/CategoryFeedback"
                ref_name = ref_path.split("/")[-1]
                ref_schema = defs.get(ref_name, {})
                schema.update(_resolve_refs(ref_schema))
            
            # Flatten allOf
            if "allOf" in schema:
                merged = {}
                for subschema in schema.pop("allOf"):
                    merged.update(_resolve_refs(subschema))
                schema.update(merged)

            # Recurse
            for k, v in schema.items():
                schema[k] = _resolve_refs(v)

            # Set nested title if looks like CategoryFeedback
            if schema.get("type") == "object" and "properties" in schema:
                if set(["rating","justification","original","correction","recommendation"]).issubset(schema["properties"].keys()):
                    schema["title"] = nested_title

        elif isinstance(schema, list):
            schema = [_resolve_refs(item) for item in schema]

        return schema

    flat_schema = _resolve_refs(raw_schema)
    flat_schema.pop("$defs", None)
    return flat_schema

def flatten_pydantic_schema(model: type[BaseModel]) -> dict:
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


def extract_feedback_df(response, metrics):
    match = re.search(r"\{.*\}", response.text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in response.text")
    response_json = json.loads(match.group(0))
    results = {}
    for metric in metrics:
        data = response_json.get(metric, {})
        results[metric] = {
            "rating": data.get("rating"),
            "justification": data.get("justification"),
            "original": data.get("original", []),
            "correction": data.get("correction", []),
            "recommendation": data.get("recommendation"),
        }
    df = _pd.DataFrame.from_dict(results, orient="index")
    df.index.name = "metric"
    df.reset_index(inplace=True)
    return df


def extract_feedback_summary(df1, df2):
    rating = float(round((df1.rating.mean() * 0.5 + df2.rating.mean() * 0.5) / 5 * 100, 2))
    justification = " ".join(df1.justification.fillna("").tolist()) + " " + " ".join(
        df2.justification.fillna("").tolist()
    )
    recommendation = " ".join(df1.recommendation.fillna("").tolist()) + " " + " ".join(
        df2.recommendation.fillna("").tolist()
    )
    originals = [item for sublist in (df1.original.tolist() + df2.original.tolist()) if sublist for item in sublist]
    corrections = [
        item for sublist in (df1.correction.tolist() + df2.correction.tolist()) if sublist for item in sublist
    ]
    return rating, justification.strip(), recommendation.strip(), originals, corrections


# =====================
# Schemas & Metrics
# =====================
output_schema_taskA = fully_flatten_pydantic_schema(TEFTaskAResponse)
output_schema_taskB = fully_flatten_pydantic_schema(TEFTaskBResponse)
judge_output_schema = flatten_pydantic_schema(TEFJudgeResponse)

metrics_taskA = [
    "task_fulfillment",
    "organization_coherence",
    "content_relevance",
    "vocabulary",
    "grammar_syntax",
    "cohesion",
    "style_adaptability",
]
metrics_taskB = [
    "task_fulfillment",
    "structure",
    "argumentation",
    "vocabulary",
    "grammar_syntax",
    "cohesion",
    "tone",
    "style_adaptability",
]


# =====================
# Request Models
# =====================
class GenerateQuestionRequest(BaseModel):
    task: Literal["A", "B"]


class EvaluateTaskARequest(BaseModel):
    task_a_question: str
    task_a_response: str


class EvaluateTaskBRequest(BaseModel):
    task_b_question: str
    task_b_response: str


class EvaluateBothRequest(BaseModel):
    task_a_question: str
    task_a_response: str
    task_b_question: str
    task_b_response: str


# =====================
# Question Generation (inlined)
# =====================
async def generate_task_a_question(client: genai.Client) -> str:
    """Generate a single Task A (narrative continuation) question using Gemini."""
    task_a_system = (
        "You are a TEF exam question generator. Create a concise French prompt for a short narrative continuation task (Task A)."
    )
    task_a_content = (
        "Generate a single Task A prompt in French for a narrative continuation.\n"
        "Constraints:\n"
        "- The student should write approximately 80–120 words.\n"
        "- Keep the scenario modern, everyday-life relevant, and culturally neutral.\n"
        "- Output only the prompt text, no quotes or extra commentary."
    )
    resp = client.models.generate_content(
        model=model_pro,
        config=types.GenerateContentConfig(
            system_instruction=task_a_system,
            response_mime_type="text/plain",
        ),
        contents=task_a_content,
    )
    text = getattr(resp, "text", "").strip()
    return text or (
        "Rédigez un court récit (80–120 mots) à partir de la situation suivante: "
        "Vous arrivez dans une nouvelle ville et rencontrez votre voisin pour la première fois."
    )


async def generate_task_b_question(client: genai.Client) -> str:
    """Generate a single Task B (opinion/argumentative letter) question using Gemini."""
    task_b_system = (
        "You are a TEF exam question generator. Create a concise French prompt for an opinion/argumentative letter task (Task B)."
    )
    task_b_content = (
        "Generate a single Task B prompt in French for an opinion/argumentative letter.\n"
        "Constraints:\n"
        "- The student should write approximately 200–250 words.\n"
        "- The topic should be contemporary and suitable for general audiences.\n"
        "- Output only the prompt text, no quotes or extra commentary."
    )
    resp = client.models.generate_content(
        model=model_pro,
        config=types.GenerateContentConfig(
            system_instruction=task_b_system,
            response_mime_type="text/plain",
        ),
        contents=task_b_content,
    )
    text = getattr(resp, "text", "").strip()
    return text or (
        "Écrivez une lettre d’opinion (200–250 mots) sur l’impact du télétravail sur la qualité de vie et la productivité."
    )


# =====================
# Routes
# =====================
@app.get("/", response_class=HTMLResponse)
async def root():
    with open("index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.get("/api/config")
async def get_config():
    return {
        "appName": settings.app_name,
        "version": settings.app_version,
        "writingTimeMinutes": settings.writing_time_minutes,
        "minWordsTaskA": settings.min_words_task_a,
        "minWordsTaskB": settings.min_words_task_b,
    }


# ---- Auth endpoints ----
@app.post("/api/auth/register", response_model=UserOut)
def register(creds: UserCredentials, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == creds.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    user = User(username=creds.username, hashed_password=get_password_hash(creds.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserOut(id=user.id, username=user.username)


@app.post("/api/auth/login", response_model=Token)
def login(creds: UserCredentials, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == creds.username).first()
    if not user or not verify_password(creds.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    token = create_access_token({"sub": str(user.id), "username": user.username})
    return Token(access_token=token)


@app.get("/api/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return UserOut(id=current_user.id, username=current_user.username)


@app.get("/api/submissions")
def list_submissions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    subs = (
        db.query(Submission)
        .filter(Submission.user_id == current_user.id)
        .order_by(Submission.created_at.desc())
        .all()
    )
    return [
        {
            "id": s.id,
            "created_at": s.created_at.isoformat(),
            "final_score": s.final_score,
            "rating_a": s.rating_a,
            "rating_b": s.rating_b,
            "task_a_question": s.task_a_question,
            "task_b_question": s.task_b_question,
            "task_a_response": s.task_a_response,
            "task_b_response": s.task_b_response,
            "judge_a": s.judge_a,
            "judge_b": s.judge_b,
            "justification_a": s.justification_a,
            "recommendation_a": s.recommendation_a,
            "originals_a": s.originals_a,
            "corrections_a": s.corrections_a,
            "justification_b": s.justification_b,
            "recommendation_b": s.recommendation_b,
            "originals_b": s.originals_b,
            "corrections_b": s.corrections_b,
        }
        for s in subs
    ]


@app.post("/api/question")
async def generate_question(
    payload: GenerateQuestionRequest, current_user: User = Depends(get_current_user)
):
    # AI-generated questions using Gemini
    if payload.task == "A":
        question = await generate_task_a_question(client)
    else:
        question = await generate_task_b_question(client)
    return {"question": question}


@app.post("/api/evaluate/task-a")
async def evaluate_task_a(
    payload: EvaluateTaskARequest, current_user: User = Depends(get_current_user)
):
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
            response_mime_type="application/json",
            response_schema=output_schema_taskA,
        ),
        contents=taskA_content_eval1,
    )
    resp_eval2_A = client.models.generate_content(
        model=model_pro,
        config=types.GenerateContentConfig(
            system_instruction=eval2_system_instruction_taskA,
            response_mime_type="application/json",
            response_schema=output_schema_taskA,
        ),
        contents=taskA_content_eval2,
    )

    # Parse Task A
    df1A = extract_feedback_df(resp_eval1_A, metrics_taskA)
    df2A = extract_feedback_df(resp_eval2_A, metrics_taskA)
    rating_A, justification_A, recommendation_A, originals_A, corrections_A = extract_feedback_summary(
        df1A, df2A
    )

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
            response_mime_type="application/json",
            response_schema=judge_output_schema,
        ),
        contents=taskA_judge_content,
    )

    return {
        "judge": json.loads(re.search(r"\{.*\}", resp_judge_A.text, re.DOTALL).group(0)),
        "rating": rating_A,
    }


@app.post("/api/evaluate/task-b")
async def evaluate_task_b(
    payload: EvaluateTaskBRequest, current_user: User = Depends(get_current_user)
):
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
            response_mime_type="application/json",
            response_schema=output_schema_taskB,
        ),
        contents=taskB_content_eval1,
    )
    resp_eval2_B = client.models.generate_content(
        model=model_pro,
        config=types.GenerateContentConfig(
            system_instruction=eval2_system_instruction_taskB,
            response_mime_type="application/json",
            response_schema=output_schema_taskB,
        ),
        contents=taskB_content_eval2,
    )
    df1B = extract_feedback_df(resp_eval1_B, metrics_taskB)
    df2B = extract_feedback_df(resp_eval2_B, metrics_taskB)
    rating_B, justification_B, recommendation_B, originals_B, corrections_B = extract_feedback_summary(
        df1B, df2B
    )
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
            response_mime_type="application/json",
            response_schema=judge_output_schema,
        ),
        contents=taskB_judge_content,
    )
    return {
        "judge": json.loads(re.search(r"\{.*\}", resp_judge_B.text, re.DOTALL).group(0)),
        "rating": rating_B,
    }


@app.post("/api/evaluate/both")
async def evaluate_both(
    payload: EvaluateBothRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Task A
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
    resp_eval1_A = client.models.generate_content(
        model=model_pro,
        config=types.GenerateContentConfig(
            system_instruction=eval1_system_instruction_taskA,
            response_mime_type="application/json",
            response_schema=output_schema_taskA,
        ),
        contents=taskA_content_eval1,
    )
    resp_eval2_A = client.models.generate_content(
        model=model_pro,
        config=types.GenerateContentConfig(
            system_instruction=eval2_system_instruction_taskA,
            response_mime_type="application/json",
            response_schema=output_schema_taskA,
        ),
        contents=taskA_content_eval2,
    )
    df1A = extract_feedback_df(resp_eval1_A, metrics_taskA)
    df2A = extract_feedback_df(resp_eval2_A, metrics_taskA)
    rating_A, justification_A, recommendation_A, originals_A, corrections_A = extract_feedback_summary(
        df1A, df2A
    )
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
            response_mime_type="application/json",
            response_schema=judge_output_schema,
        ),
        contents=taskA_judge_content,
    )
    judge_A = json.loads(re.search(r"\{.*\}", resp_judge_A.text, re.DOTALL).group(0))

    # Task B
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
            response_mime_type="application/json",
            response_schema=output_schema_taskB,
        ),
        contents=taskB_content_eval1,
    )
    resp_eval2_B = client.models.generate_content(
        model=model_pro,
        config=types.GenerateContentConfig(
            system_instruction=eval2_system_instruction_taskB,
            response_mime_type="application/json",
            response_schema=output_schema_taskB,
        ),
        contents=taskB_content_eval2,
    )
    df1B = extract_feedback_df(resp_eval1_B, metrics_taskB)
    df2B = extract_feedback_df(resp_eval2_B, metrics_taskB)
    rating_B, justification_B, recommendation_B, originals_B, corrections_B = extract_feedback_summary(
        df1B, df2B
    )
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
            response_mime_type="application/json",
            response_schema=judge_output_schema,
        ),
        contents=taskB_judge_content,
    )
    judge_B = json.loads(re.search(r"\{.*\}", resp_judge_B.text, re.DOTALL).group(0))

    final_score = int(round((rating_A * 0.4 + rating_B * 0.6) * 6.99))

    # Persist submission (store Judge LLM justification/recommendation and error analysis)
    sub = Submission(
        user_id=current_user.id,
        task_a_question=payload.task_a_question,
        task_a_response=payload.task_a_response,
        task_b_question=payload.task_b_question,
        task_b_response=payload.task_b_response,
        rating_a=rating_A,
        rating_b=rating_B,
        final_score=final_score,
        judge_a=judge_A,
        judge_b=judge_B,
        justification_a=judge_A.get("justification"),
        recommendation_a=judge_A.get("recommendation"),
        originals_a=judge_A.get("originals"),
        corrections_a=judge_A.get("corrections"),
        justification_b=judge_B.get("justification"),
        recommendation_b=judge_B.get("recommendation"),
        originals_b=judge_B.get("originals"),
        corrections_b=judge_B.get("corrections"),
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)

    return {
        "submission_id": sub.id,
        "taskA": {"judge": judge_A, "rating": rating_A},
        "taskB": {"judge": judge_B, "rating": rating_B},
        "finalScore": final_score,
    }


if __name__ == "__main__":
    webbrowser.open(f"http://{settings.host}:{settings.port}")
    uvicorn.run(app, host=settings.host, port=settings.port)

