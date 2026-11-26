from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field

from app.services.question_bank import QuestionType


class QuestionOptionSchema(BaseModel):
    """Serialized option presented to the client."""

    id: str
    label: str
    description: str | None = None


class QuestionSchema(BaseModel):
    """Serialized assessment question."""

    id: str
    prompt: str
    question_type: QuestionType
    category: str
    help_text: str | None = None
    options: list[QuestionOptionSchema] = Field(default_factory=list)
    min_value: int | None = None
    max_value: int | None = None
    min_label: str | None = None
    max_label: str | None = None
    max_selections: int | None = None
    is_adaptive: bool = False


class AssessmentResponseItem(BaseModel):
    """Saved answer for a single question."""

    question_id: str
    answer_value: Any
    answered_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AssessmentProgressSchema(BaseModel):
    """Progress metrics for an assessment session."""

    answered_count: int
    total_questions: int
    progress_percent: int
    next_question_id: str | None


class AssessmentSessionDetail(BaseModel):
    """Full assessment session state for starting, resuming, or reviewing."""

    id: int
    status: Literal["in_progress", "completed"]
    current_question_id: str | None
    started_at: datetime
    updated_at: datetime
    completed_at: datetime | None
    questions: list[QuestionSchema]
    responses: dict[str, Any]
    progress: AssessmentProgressSchema


class StartSessionRequest(BaseModel):
    """Optional configuration when starting or resuming an assessment session."""

    resume_if_active: bool = True


class SaveResponseRequest(BaseModel):
    """Payload to save or update a single question response."""

    question_id: str = Field(min_length=1, max_length=80)
    answer_value: Any
    current_question_id: str | None = Field(default=None, max_length=80)
