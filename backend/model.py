from typing import List, Final
from pydantic import BaseModel, Field
import datetime

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

class EST5EDT(datetime.tzinfo):

    def utcoffset(self, dt):
        return datetime.timedelta(hours=-5) + self.dst(dt)

    def dst(self, dt):
        d = datetime.datetime(dt.year, 3, 8)        #2nd Sunday in March
        self.dston = d + datetime.timedelta(days=6-d.weekday())
        d = datetime.datetime(dt.year, 11, 1)       #1st Sunday in Nov
        self.dstoff = d + datetime.timedelta(days=6-d.weekday())
        if self.dston <= dt.replace(tzinfo=None) < self.dstoff:
            return datetime.timedelta(hours=1)
        else:
            return datetime.timedelta(0)

    def tzname(self, dt):
        return 'EST5EDT'


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now(tz=EST5EDT()))
    submissions = relationship("Submission", back_populates="user")


class Submission(Base):
    __tablename__ = "submissions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    task_a_question = Column(String)
    task_a_response = Column(String)
    task_b_question = Column(String)
    task_b_response = Column(String)
    rating_a = Column(Float)
    rating_b = Column(Float)
    final_score = Column(Integer)
    judge_a = Column(JSON)
    judge_b = Column(JSON)
    # New fields for recommendations, justifications, and error analysis
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
    created_at = Column(DateTime, default=datetime.datetime.now(tz=EST5EDT()))
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
        description="Score from 1 to 5 in increments of 0.5. Required."
    )
    justification: str = Field(
        ...,
        description="Brief justification and feedback for the score in English! Required."
    )
    original: List[str] = Field(
        ...,
        description="The original text that contains the error in French. Required."
    )
    correction: List[str] = Field(
        ...,
        description="The corrected text in French. Required."
    )
    recommendation: str = Field(
        ...,
        description="Actionable recommendation for the description."
    )


class TEFTaskAResponse(BaseModel):
    task_fulfillment: CategoryFeedback = Field(
        ...,
        description="Evaluation for Task Fulfillment. Required."
    )
    organization_coherence: CategoryFeedback = Field(
        ...,
        description="Evaluation for Organization & Coherence. Required."
    )
    content_relevance: CategoryFeedback = Field(
        ...,
        description="Evaluation for Content Relevance. Required."
    )
    vocabulary: CategoryFeedback = Field(
        ...,
        description="Evaluation for Vocabulary. Required."
    )
    grammar_syntax: CategoryFeedback = Field(
        ...,
        description="Evaluation for Grammar & Syntax. Required."
    )
    cohesion: CategoryFeedback = Field(
        ...,
        description="Evaluation for Cohesion. Required."
    )
    style_adaptability: CategoryFeedback = Field(
        ...,
        description="Evaluation for Style & Adaptability. Required."
    )


class TEFTaskBResponse(BaseModel):
    task_fulfillment: CategoryFeedback = Field(
        ...,
        description="Evaluation for Task Fulfillment. Required."
    )
    structure: CategoryFeedback = Field(
        ...,
        description="Evaluation for Structure. Required."
    )
    argumentation: CategoryFeedback = Field(
        ...,
        description="Evaluation for Argumentation. Required."
    )
    vocabulary: CategoryFeedback = Field(
        ...,
        description="Evaluation for Vocabulary. Required."
    )
    grammar_syntax: CategoryFeedback = Field(
        ...,
        description="Evaluation for Grammar & Syntax. Required."
    )
    cohesion: CategoryFeedback = Field(
        ...,
        description="Evaluation for Cohesion. Required."
    )
    tone: CategoryFeedback = Field(
        ...,
        description="Evaluation for Tone. Required."
    )
    style_adaptability: CategoryFeedback = Field(
        ...,
        description="Evaluation for Style & Adaptability. Required."
    )


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
        description="List of original texts for error analysis."
    )
    corrections: List[str] = Field(
        ...,
        description="List of corrected texts for error analysis."
    )
