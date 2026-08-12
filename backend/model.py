import datetime
from typing import List
from zoneinfo import ZoneInfo

from pydantic import BaseModel, Field

# --- SQLAlchemy (DB models) ---
from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Session

# Read DB URL from app settings
from config import settings

# SQLite engine/session (simple local file by default)
SQLALCHEMY_DATABASE_URL = settings.database_url
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Replaces a hand-rolled EST5EDT tzinfo whose DST boundary arithmetic was wrong
# in some years. Needs the `tzdata` package on Windows.
EASTERN = ZoneInfo("America/Toronto")


def now_eastern() -> datetime.datetime:
    """Current Eastern time.

    Passed to Column(default=...) as a *callable*. The previous code passed
    ``datetime.now(...)`` — the already-evaluated result — so every row created
    by a given process shared one identical timestamp. That silently broke
    `ORDER BY created_at DESC`, which the dashboard and
    /api/generate-improved-answer both rely on to find the newest submission.
    """
    return datetime.datetime.now(tz=EASTERN)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=now_eastern)
    submissions = relationship("Submission", back_populates="user")


class Submission(Base):
    __tablename__ = "submissions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    task_a_question = Column(String)
    task_a_response = Column(String)
    task_b_question = Column(String)
    task_b_response = Column(String)
    # --- Scoring (see scoring.py; every score column is on the 0-450 scale that
    # IRCC reads, never the /699 headline figure the attestation also shows) ---
    # Raw 1-5 evaluator means, per section. These are the source of truth: the
    # full report is recomputed from them at read time so that a change to the
    # calibration curve applies to past submissions too. The derived columns
    # below are stored anyway so scores stay queryable without importing the app.
    rating_a = Column(Float)
    rating_b = Column(Float)
    combined_rating = Column(Float)      # 40% A + 60% B, 1-5
    score = Column(Integer)              # /450 — the number IRCC wants
    nclc = Column(Integer)               # NCLC/CLB writing level, 0 if below 4
    cefr = Column(String(8))             # indicative CECRL band
    # Indicative per-section breakdown: the exam reports one score, but knowing
    # which section is holding the candidate back is the point of practising.
    score_a = Column(Integer)
    score_b = Column(Integer)
    nclc_a = Column(Integer)
    nclc_b = Column(Integer)

    # --- Feedback ---
    judge_a = Column(JSON)
    judge_b = Column(JSON)
    # Per-criterion breakdown: the merged rating, prose and error pairs for each
    # of the eight assessment criteria. Previously only the mean survived the
    # pipeline, so the UI could say "3.4/5" but never which criterion cost the
    # points — which is the only part a candidate can act on.
    criteria_a = Column(JSON)
    criteria_b = Column(JSON)
    # Recommendations, justifications, and error analysis
    justification_a = Column(String)
    recommendation_a = Column(String)
    originals_a = Column(JSON)
    corrections_a = Column(JSON)
    justification_b = Column(String)
    recommendation_b = Column(String)
    originals_b = Column(JSON)
    corrections_b = Column(JSON)
    # AI-improved answers
    ai_improved_answer_taskA = Column(String)
    ai_improved_answer_taskB = Column(String)
    created_at = Column(DateTime, default=now_eastern, index=True)
    user = relationship("User", back_populates="submissions")


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class CategoryFeedback(BaseModel):
    rating: float = Field(
        ...,
        ge=1.0,
        le=5.0,
        description="Score from 1 to 5, in increments of 0.1. Required."
    )
    justification: str = Field(
        ...,
        description="Brief justification and feedback for the score, in English. Required."
    )
    original: List[str] = Field(
        ...,
        description="Every excerpt of the candidate's French text that contains an error "
                    "for this category. Empty list if there are none. Required."
    )
    correction: List[str] = Field(
        ...,
        description="The corrected French for each entry in `original`, in the same order "
                    "and with the same length. Required."
    )
    recommendation: str = Field(
        ...,
        description="One actionable recommendation for improving this category, in English."
    )


# The eight criteria below mirror the assessment criteria Le français des affaires
# publishes for the TEF expression écrite. Any change here must be mirrored in
# metrics_taskA / metrics_taskB in run.py, in the criteria list inside the prompt
# text, and in tests/test_script.py — otherwise metrics silently come back None.
class TEFTaskAResponse(BaseModel):
    task_fulfillment: CategoryFeedback = Field(
        ...,
        description="Task fulfilment: continues the article, meets the 80-word minimum, "
                    "does not recopy or summarise the opening. Required."
    )
    content_relevance: CategoryFeedback = Field(
        ...,
        description="Relevance and richness of the information added. Required."
    )
    organization_coherence: CategoryFeedback = Field(
        ...,
        description="Internal coherence: logical development in paragraphs. Required."
    )
    cohesion: CategoryFeedback = Field(
        ...,
        description="Textual and sentence cohesion: connectors, anaphora, tense sequencing. Required."
    )
    vocabulary: CategoryFeedback = Field(
        ...,
        description="Range and precision of vocabulary. Required."
    )
    grammar_syntax: CategoryFeedback = Field(
        ...,
        description="Grammar and syntax: conjugation, agreement, sentence construction. Required."
    )
    spelling_punctuation: CategoryFeedback = Field(
        ...,
        description="Orthographe et ponctuation: spelling, accents, punctuation. Required."
    )
    register_tone: CategoryFeedback = Field(
        ...,
        description="Register: sustains the neutral, factual, third-person press register. Required."
    )


class TEFTaskBResponse(BaseModel):
    task_fulfillment: CategoryFeedback = Field(
        ...,
        description="Task fulfilment: addresses the statement, states and defends a position, "
                    "meets the 200-word minimum. Required."
    )
    argumentation: CategoryFeedback = Field(
        ...,
        description="Quality of the arguments: development, detail, illustration. Required."
    )
    structure: CategoryFeedback = Field(
        ...,
        description="Internal coherence: a clear line of argument across paragraphs. Required."
    )
    cohesion: CategoryFeedback = Field(
        ...,
        description="Textual and sentence cohesion: connectors, transitions, referencing. Required."
    )
    vocabulary: CategoryFeedback = Field(
        ...,
        description="Range and precision of vocabulary. Required."
    )
    grammar_syntax: CategoryFeedback = Field(
        ...,
        description="Grammar and syntax: conjugation, agreement, sentence construction. Required."
    )
    spelling_punctuation: CategoryFeedback = Field(
        ...,
        description="Orthographe et ponctuation: spelling, accents, punctuation. Required."
    )
    register_tone: CategoryFeedback = Field(
        ...,
        description="Register and tone: consistent, appropriately formal, respectful. Required."
    )


# French display names for the criteria, sent to the UI with the per-criterion
# breakdown. All user-facing copy in this app is French; keeping the labels next
# to the models they name stops the frontend from hard-coding a second list that
# drifts when a criterion is renamed.
CRITERION_LABELS: dict[str, str] = {
    "task_fulfillment": "Respect de la consigne",
    "content_relevance": "Pertinence des informations",
    "organization_coherence": "Cohérence interne",
    "argumentation": "Qualité de l'argumentation",
    "structure": "Cohérence interne",
    "cohesion": "Cohésion du texte et de la phrase",
    "vocabulary": "Lexique et variété des phrases",
    "grammar_syntax": "Grammaire et syntaxe",
    "spelling_punctuation": "Orthographe et ponctuation",
    "register_tone": "Registre et ton",
}


class TEFJudgeResponse(BaseModel):
    justification: str = Field(
        ...,
        description="Justification for the evaluation in English. Required."
    )
    recommendation: str = Field(
        ...,
        description="Recommendation for the evaluation in English. Required."
    )
    originals: List[str] = Field(
        ...,
        description="List of original French excerpts for error analysis."
    )
    corrections: List[str] = Field(
        ...,
        description="Corrected French, index-aligned with `originals` and the same length."
    )
