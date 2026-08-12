import copy
import json
import logging
import os
import re
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Literal, Optional

import uvicorn
import webbrowser
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ai_client import DEFAULT_MODELS, AIError, UnifiedAIClient
from config import settings
from model import (
    Base,
    CRITERION_LABELS,
    SessionLocal,
    Submission,
    TEFJudgeResponse,
    TEFTaskAResponse,
    TEFTaskBResponse,
    User,
    engine,
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
from questions_taskA import QUESTIONS_TASK_A
from questions_taskB import QUESTIONS_TASK_B
from prompt_answer_generation import (
    answer_system_instruction_taskA,
    answer_system_instruction_taskB,
    answer_taskA_prompt,
    answer_taskB_prompt,
)
import scoring

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =====================
# Auth & Database Setup
# =====================

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
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCredentials(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str


def get_current_user(
    token: Optional[str] = None,
    request: Request = None,
    db: Session = Depends(get_db),
) -> User:
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Fail fast instead of at the first login attempt.
    if not SECRET_KEY:
        raise RuntimeError(
            "SECRET_KEY is not set. Create backend/.env with a SECRET_KEY value "
            '(generate one with: python -c "import secrets; print(secrets.token_hex(32))").'
        )
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.username == "testing").first():
            db.add(User(username="testing", hashed_password=get_password_hash("testing")))
            db.commit()
    finally:
        db.close()
    yield


app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================
# AI Client Dependency
# =====================
def _env_key_for(provider: str) -> str:
    """Return the environment-variable API key for the given provider."""
    return os.getenv(
        {"google": "GOOGLE_API_KEY", "openai": "OPENAI_API_KEY",
         "anthropic": "ANTHROPIC_API_KEY", "openrouter": "OPENROUTER_API_KEY"}.get(provider, ""),
        "",
    )


def get_ai_client(request: Request) -> UnifiedAIClient:
    """FastAPI dependency: builds a UnifiedAIClient from per-request headers,
    falling back to environment variables and application defaults."""
    provider = (
        request.headers.get("X-AI-Provider")
        or os.getenv("AI_PROVIDER", settings.ai_provider)
    )
    api_key = request.headers.get("X-AI-Key") or _env_key_for(provider)
    model = (
        request.headers.get("X-AI-Model")
        or DEFAULT_MODELS.get(provider, settings.ai_model_pro)
    )
    if not api_key:
        raise HTTPException(
            status_code=400,
            detail=(
                f"No API key found for provider '{provider}'. "
                "Pass the X-AI-Key header from the UI or set the corresponding "
                "environment variable (GOOGLE_API_KEY / OPENAI_API_KEY / "
                "ANTHROPIC_API_KEY / OPENROUTER_API_KEY)."
            ),
        )
    try:
        return UnifiedAIClient(provider=provider, api_key=api_key, model=model)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


# =====================
# Utilities for schemas
# =====================

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


# Matches frontend/src/lib/text.js so the word count the candidate sees while
# writing is the same one the evaluator is told about. `.split()` alone counted
# bare punctuation ("—") as words.
_WORD_RE = re.compile(r"[^\W_]+(?:['’-][^\W_]+)*", re.UNICODE)


def count_words(text: str) -> int:
    return len(_WORD_RE.findall(text or ""))


def parse_json_response(response, label: str) -> dict:
    """Extract the JSON object from a provider response.

    Previously the judge call sites did `re.search(...).group(0)` with no None
    check, so a truncated or non-JSON response raised an opaque AttributeError
    and surfaced as a 500 after several minutes of paid API calls.
    """
    text = getattr(response, "text", "") or ""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        logger.error("%s: no JSON object in model response. First 500 chars: %s", label, text[:500])
        raise HTTPException(
            status_code=502,
            detail=(
                f"The AI model did not return valid JSON for {label}. This usually means the "
                "response was truncated or the model ignored the schema. Please try again, "
                "or switch to a more capable model."
            ),
        )
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError as exc:
        logger.error("%s: malformed JSON (%s). First 500 chars: %s", label, exc, text[:500])
        raise HTTPException(
            status_code=502,
            detail=(
                f"The AI model returned malformed JSON for {label}. Please try again, "
                "or switch to a more capable model."
            ),
        ) from exc


def extract_feedback_df(response, metrics, label: str):
    response_json = parse_json_response(response, label)
    rows = []
    missing = []
    for metric in metrics:
        data = response_json.get(metric) or {}
        if not data:
            missing.append(metric)
        rows.append({
            "metric": metric,
            "rating": data.get("rating"),
            "justification": data.get("justification"),
            "original": data.get("original", []),
            "correction": data.get("correction", []),
            "recommendation": data.get("recommendation"),
        })
    if len(missing) == len(metrics):
        raise HTTPException(
            status_code=502,
            detail=(
                f"The AI model returned none of the expected criteria for {label}. "
                "Please try again, or switch to a more capable model."
            ),
        )
    if missing:
        logger.warning("%s: model omitted criteria %s", label, missing)
    return rows


def extract_feedback_summary(rows1, rows2):
    def avg_rating(rows):
        ratings = [r["rating"] for r in rows if r["rating"] is not None]
        # Clamp: a stray out-of-range rating would otherwise skew the mean.
        ratings = [max(1.0, min(5.0, float(r))) for r in ratings]
        return sum(ratings) / len(ratings) if ratings else None

    avg1, avg2 = avg_rating(rows1), avg_rating(rows2)
    present = [a for a in (avg1, avg2) if a is not None]
    if not present:
        # Previously this silently produced 0.0, which the old curve turned into
        # a plausible-looking score instead of an error.
        raise HTTPException(
            status_code=502,
            detail="The AI model returned no usable ratings. Please try again.",
        )
    rating = float(round(sum(present) / len(present), 2))

    def join_field(rows, field):
        return " ".join(r[field] or "" for r in rows).strip()

    justification = (join_field(rows1, "justification") + " " + join_field(rows2, "justification")).strip()
    recommendation = (join_field(rows1, "recommendation") + " " + join_field(rows2, "recommendation")).strip()

    originals = [item for r in rows1 + rows2 for item in (r["original"] or [])]
    corrections = [item for r in rows1 + rows2 for item in (r["correction"] or [])]

    return rating, justification, recommendation, originals, corrections


def merge_criteria(rows1, rows2, metrics):
    """Merge the two evaluators into one record per assessment criterion.

    The pipeline used to collapse both evaluators straight to a single mean, so
    everything below the headline number was lost: a candidate could be told
    "3.4/5" with no way to see that spelling was the criterion dragging it down.
    Each row keeps both evaluators' ratings alongside their 50/50 mean, since a
    wide split between the encouraging and the critical evaluator is itself
    useful signal that the criterion is borderline.
    """
    by_metric1 = {r["metric"]: r for r in rows1}
    by_metric2 = {r["metric"]: r for r in rows2}

    merged = []
    for metric in metrics:
        r1 = by_metric1.get(metric) or {}
        r2 = by_metric2.get(metric) or {}

        def _rating(row):
            value = row.get("rating")
            return None if value is None else max(1.0, min(5.0, float(value)))

        ratings = [v for v in (_rating(r1), _rating(r2)) if v is not None]
        justifications = [r.get("justification") for r in (r1, r2) if r.get("justification")]
        recommendations = [r.get("recommendation") for r in (r1, r2) if r.get("recommendation")]
        originals = [item for r in (r1, r2) for item in (r.get("original") or [])]
        corrections = [item for r in (r1, r2) for item in (r.get("correction") or [])]

        merged.append({
            "metric": metric,
            "label": CRITERION_LABELS.get(metric, metric),
            "rating": round(sum(ratings) / len(ratings), 2) if ratings else None,
            "ratingEval1": _rating(r1),
            "ratingEval2": _rating(r2),
            "justification": " ".join(justifications).strip() or None,
            "recommendation": " ".join(recommendations).strip() or None,
            "originals": originals,
            "corrections": corrections,
        })
    return merged


def build_judge_input(criteria: list[dict]) -> tuple[str, str, str, str]:
    """Build the judge's view of the merged evaluation from `merge_criteria`.

    Feeding the judge a blind concatenation of both evaluators' prose (the
    previous behaviour) left it "consolidating" an undifferentiated wall of
    text with no way to tell which sentence was about vocabulary versus
    grammar. This keeps the per-criterion label `merge_criteria` already
    computes, and numbers each original/correction pair explicitly instead of
    relying on two separately-stringified lists staying aligned by position.
    `CRITERION_LABELS` is French/UI-facing, so criteria are labelled here with
    the plain English metric name instead, to match the judge's English
    justification and recommendation prose.
    """
    justification_lines, recommendation_lines = [], []
    originals, corrections = [], []
    for row in criteria:
        label = row["metric"].replace("_", " ")
        if row["justification"]:
            justification_lines.append(f"- {label}: {row['justification']}")
        if row["recommendation"]:
            recommendation_lines.append(f"- {label}: {row['recommendation']}")
        originals.extend(row["originals"])
        corrections.extend(row["corrections"])

    def numbered(items: list[str]) -> str:
        return "\n".join(f"{i + 1}. {item}" for i, item in enumerate(items)) or "(none)"

    return (
        "\n".join(justification_lines) or "(no justification returned)",
        "\n".join(recommendation_lines) or "(no recommendation returned)",
        numbered(originals),
        numbered(corrections),
    )


# =====================
# Schemas & Metrics
# =====================
output_schema_taskA = fully_flatten_pydantic_schema(TEFTaskAResponse)
output_schema_taskB = fully_flatten_pydantic_schema(TEFTaskBResponse)
judge_output_schema = flatten_pydantic_schema(TEFJudgeResponse)

# These must match the field names on TEFTaskAResponse / TEFTaskBResponse in
# model.py and the criteria enumerated in the prompt text, or the corresponding
# metric silently comes back None.
metrics_taskA = [
    "task_fulfillment",
    "content_relevance",
    "organization_coherence",
    "cohesion",
    "vocabulary",
    "grammar_syntax",
    "spelling_punctuation",
    "register_tone",
]
metrics_taskB = [
    "task_fulfillment",
    "argumentation",
    "structure",
    "cohesion",
    "vocabulary",
    "grammar_syntax",
    "spelling_punctuation",
    "register_tone",
]

assert set(metrics_taskA) == set(TEFTaskAResponse.model_fields), "Task A metrics/model drift"
assert set(metrics_taskB) == set(TEFTaskBResponse.model_fields), "Task B metrics/model drift"


# =====================
# Request Models
# =====================
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


class GenerateImprovedAnswerRequest(BaseModel):
    taskType: Literal["A", "B"]
    question: str
    userAnswer: str


# =====================
# Evaluation pipeline
# =====================
def _evaluate_task(
    ai_client: UnifiedAIClient,
    *,
    label: str,
    question: str,
    response_text: str,
    eval1_system: str,
    eval1_template: str,
    eval2_system: str,
    eval2_template: str,
    judge_system: str,
    judge_template: str,
    output_schema: dict,
    metrics: list[str],
):
    """Two independent evaluators plus a judge, for one section.

    Mirrors the real exam, where each script is marked by two independent
    correctors. Extracted here so /evaluate/task-a, /task-b and /both share one
    implementation instead of three copies that could drift apart.
    """
    word_count = count_words(response_text)

    content_eval1 = eval1_template.format(
        question=question, response=response_text, word_count=word_count
    )
    content_eval2 = eval2_template.format(
        question=question, response=response_text, word_count=word_count
    )

    resp_eval1 = ai_client.generate_json(
        system=eval1_system, content=content_eval1, schema=output_schema
    )
    resp_eval2 = ai_client.generate_json(
        system=eval2_system, content=content_eval2, schema=output_schema
    )

    rows1 = extract_feedback_df(resp_eval1, metrics, f"{label} evaluator 1")
    rows2 = extract_feedback_df(resp_eval2, metrics, f"{label} evaluator 2")
    rating, *_ = extract_feedback_summary(rows1, rows2)
    criteria = merge_criteria(rows1, rows2, metrics)

    judge_justification, judge_recommendation, judge_originals, judge_corrections = build_judge_input(
        criteria
    )
    judge_content = judge_template.format(
        justification=judge_justification,
        recommendations=judge_recommendation,
        originals=judge_originals,
        corrections=judge_corrections,
    )
    resp_judge = ai_client.generate_json(
        system=judge_system, content=judge_content, schema=judge_output_schema
    )
    judge = parse_json_response(resp_judge, f"{label} judge")
    return judge, rating, criteria


def evaluate_task_a_pipeline(ai_client, question, response_text):
    return _evaluate_task(
        ai_client,
        label="Task A",
        question=question,
        response_text=response_text,
        eval1_system=eval1_system_instruction_taskA,
        eval1_template=eval1_taskA_prompt,
        eval2_system=eval2_system_instruction_taskA,
        eval2_template=eval2_taskA_prompt,
        judge_system=judge_system_instruction_taskA,
        judge_template=judge_prompt_taskA,
        output_schema=output_schema_taskA,
        metrics=metrics_taskA,
    )


def evaluate_task_b_pipeline(ai_client, question, response_text):
    return _evaluate_task(
        ai_client,
        label="Task B",
        question=question,
        response_text=response_text,
        eval1_system=eval1_system_instruction_taskB,
        eval1_template=eval1_taskB_prompt,
        eval2_system=eval2_system_instruction_taskB,
        eval2_template=eval2_taskB_prompt,
        judge_system=judge_system_instruction_taskB,
        judge_template=judge_prompt_taskB,
        output_schema=output_schema_taskB,
        metrics=metrics_taskB,
    )


def submission_scores(sub: Submission) -> dict:
    """Full /450 score breakdown for a stored submission.

    Recomputed from the stored 1-5 ratings rather than read back from the derived
    columns, so that a change to the calibration curve in scoring.py applies to
    every past submission instead of leaving a mix of old and new numbers in the
    history list. The derived columns are still written on insert (see
    `apply_scores`) so the scores can be queried straight from SQLite.
    """
    if sub.rating_a is None or sub.rating_b is None:
        return {"score": sub.score, "scoreMax": scoring.SCALE_MAX, "nclc": sub.nclc}
    return scoring.score_report(sub.rating_a, sub.rating_b)


def apply_scores(sub: Submission, scores: dict) -> None:
    """Write the derived score columns onto a Submission."""
    sub.combined_rating = scores["rating"]
    sub.score = scores["score"]
    sub.nclc = scores["nclc"]
    sub.cefr = scores["cefr"]
    sub.score_a = scores["sectionA"]["score"]
    sub.score_b = scores["sectionB"]["score"]
    sub.nclc_a = scores["sectionA"]["nclc"]
    sub.nclc_b = scores["sectionB"]["nclc"]


# =====================
# Routes
# =====================
# NOTE: every route that calls the AI is a plain `def`, not `async def`.
# The provider SDKs are synchronous; running them in an `async def` handler
# blocks the event loop for the several minutes an evaluation takes, freezing
# the whole server. `def` handlers run in FastAPI's threadpool instead.

@app.get("/api/config")
def get_config():
    return {
        "appName": settings.app_name,
        "version": settings.app_version,
        "writingTimeMinutes": settings.writing_time_minutes,
        "sectionAMinutes": settings.section_a_minutes,
        "sectionBMinutes": settings.section_b_minutes,
        "minWordsTaskA": settings.min_words_task_a,
        "minWordsTaskB": settings.min_words_task_b,
        "recommendedWordsTaskA": settings.recommended_words_task_a,
        "recommendedWordsTaskB": settings.recommended_words_task_b,
        # Scoring is reported on the 0-450 scale only — the "équivalence ancien
        # score" column, which is the one IRCC accepts.
        "scoreMax": scoring.SCALE_MAX,
        "expressEntryThreshold": scoring.EXPRESS_ENTRY_THRESHOLD,
        "expressEntryNclc": scoring.EXPRESS_ENTRY_NCLC,
        "nclcBands": [
            {"floor": floor, "ceiling": ceiling, "nclc": level}
            for floor, ceiling, level in scoring.NCLC_BANDS
        ],
        "defaultModels": DEFAULT_MODELS,
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
        # Secondary sort on the monotonic primary key: it keeps ordering stable
        # for rows written before created_at was fixed to a per-row timestamp.
        .order_by(Submission.created_at.desc(), Submission.id.desc())
        .all()
    )
    return [
        {
            "id": s.id,
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "rating_a": s.rating_a,
            "rating_b": s.rating_b,
            "scores": submission_scores(s),
            "criteria_a": s.criteria_a,
            "criteria_b": s.criteria_b,
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
            "ai_improved_answer_taskA": s.ai_improved_answer_taskA,
            "ai_improved_answer_taskB": s.ai_improved_answer_taskB,
        }
        for s in subs
    ]


@app.get("/api/questions")
def list_questions():
    return {"taskA": QUESTIONS_TASK_A, "taskB": QUESTIONS_TASK_B}


@app.post("/api/evaluate/task-a")
def evaluate_task_a(
    payload: EvaluateTaskARequest,
    current_user: User = Depends(get_current_user),
    ai_client: UnifiedAIClient = Depends(get_ai_client),
):
    try:
        judge, rating, criteria = evaluate_task_a_pipeline(
            ai_client, payload.task_a_question, payload.task_a_response
        )
    except AIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {
        "judge": judge,
        "rating": rating,
        "criteria": criteria,
        "section": scoring.section_report(rating),
    }


@app.post("/api/evaluate/task-b")
def evaluate_task_b(
    payload: EvaluateTaskBRequest,
    current_user: User = Depends(get_current_user),
    ai_client: UnifiedAIClient = Depends(get_ai_client),
):
    try:
        judge, rating, criteria = evaluate_task_b_pipeline(
            ai_client, payload.task_b_question, payload.task_b_response
        )
    except AIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {
        "judge": judge,
        "rating": rating,
        "criteria": criteria,
        "section": scoring.section_report(rating),
    }


@app.post("/api/evaluate/both")
def evaluate_both(
    payload: EvaluateBothRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    ai_client: UnifiedAIClient = Depends(get_ai_client),
):
    try:
        judge_A, rating_A, criteria_A = evaluate_task_a_pipeline(
            ai_client, payload.task_a_question, payload.task_a_response
        )
        judge_B, rating_B, criteria_B = evaluate_task_b_pipeline(
            ai_client, payload.task_b_question, payload.task_b_response
        )
    except AIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    scores = scoring.score_report(rating_A, rating_B)

    sub = Submission(
        user_id=current_user.id,
        task_a_question=payload.task_a_question,
        task_a_response=payload.task_a_response,
        task_b_question=payload.task_b_question,
        task_b_response=payload.task_b_response,
        rating_a=rating_A,
        rating_b=rating_B,
        judge_a=judge_A,
        judge_b=judge_B,
        criteria_a=criteria_A,
        criteria_b=criteria_B,
        justification_a=judge_A.get("justification"),
        recommendation_a=judge_A.get("recommendation"),
        originals_a=judge_A.get("originals"),
        corrections_a=judge_A.get("corrections"),
        justification_b=judge_B.get("justification"),
        recommendation_b=judge_B.get("recommendation"),
        originals_b=judge_B.get("originals"),
        corrections_b=judge_B.get("corrections"),
    )
    apply_scores(sub, scores)
    db.add(sub)
    db.commit()
    db.refresh(sub)

    return {
        "submission_id": sub.id,
        "taskA": {
            "judge": judge_A,
            "rating": rating_A,
            "criteria": criteria_A,
            "section": scores["sectionA"],
        },
        "taskB": {
            "judge": judge_B,
            "rating": rating_B,
            "criteria": criteria_B,
            "section": scores["sectionB"],
        },
        "scores": scores,
    }


@app.post("/api/generate-improved-answer")
def generate_improved_answer(
    payload: GenerateImprovedAnswerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    ai_client: UnifiedAIClient = Depends(get_ai_client),
):
    """Generate an improved version of the user's answer."""
    if payload.taskType == "A":
        system_instruction = answer_system_instruction_taskA
        prompt_template = answer_taskA_prompt
    else:
        system_instruction = answer_system_instruction_taskB
        prompt_template = answer_taskB_prompt

    formatted_prompt = prompt_template.format(user_answer=payload.userAnswer)

    try:
        improved_answer = ai_client.generate_text(
            system=system_instruction, content=formatted_prompt
        ).text
    except AIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001 — surface provider errors, don't swallow them
        logger.exception("Error generating improved answer")
        raise HTTPException(
            status_code=502, detail=f"Failed to generate improved answer: {exc}"
        ) from exc

    # Attach to the newest submission. The id tiebreaker matters: created_at was
    # previously identical across every row written by a process, so ordering on
    # it alone could attach the answer to the wrong submission.
    recent_submission = (
        db.query(Submission)
        .filter(Submission.user_id == current_user.id)
        .order_by(Submission.created_at.desc(), Submission.id.desc())
        .first()
    )
    if recent_submission:
        if payload.taskType == "A":
            recent_submission.ai_improved_answer_taskA = improved_answer
        else:
            recent_submission.ai_improved_answer_taskB = improved_answer
        db.commit()

    return {"improvedAnswer": improved_answer}


if __name__ == "__main__":
    webbrowser.open(f"http://{settings.host}:{settings.port}")
    uvicorn.run(app, host=settings.host, port=settings.port)
