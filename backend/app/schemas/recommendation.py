from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ScoreBreakdown(BaseModel):
    interest_alignment: int = Field(ge=0, le=100)
    skill_feasibility: int = Field(ge=0, le=100)
    methodology_fit: int = Field(ge=0, le=100)
    semantic_similarity: int = Field(ge=0, le=100)
    explanation: str


class TopicRecommendation(BaseModel):
    id: str
    title: str
    description: str
    keywords: list[str]
    domain_tags: list[str]
    methodology_tags: list[str]
    min_experience_level: str
    min_weekly_hours: int
    hybrid_score: int = Field(ge=0, le=100)
    score_breakdown: ScoreBreakdown
    is_bookmarked: bool = False
    user_rating: int | None = None


class RecommendationSetResponse(BaseModel):
    id: int
    user_id: int
    interest_profile_id: int
    methodology_note: str
    results: list[TopicRecommendation]
    created_at: datetime
    updated_at: datetime


class BookmarkCreateRequest(BaseModel):
    topic_id: str = Field(min_length=1, max_length=80)


class BookmarkResponse(BaseModel):
    id: int
    topic_id: str
    title: str
    domain_tags: list[str]
    created_at: datetime


class FeedbackUpsertRequest(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=1000)


class FeedbackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    topic_id: str
    rating: int
    comment: str | None
    created_at: datetime
    updated_at: datetime
