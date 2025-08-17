from typing import List, Optional, Tuple
from pydantic import BaseModel, Field
import copy


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
