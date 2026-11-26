from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ContributionItem(BaseModel):
    """Single explainable signal contributing to a domain or dimension score."""

    source: str
    reason: str
    weight: float


class ScoreEntry(BaseModel):
    """Normalized 0-100 score with explainable contributions."""

    key: str
    label: str
    score: int
    contributions: list[ContributionItem]


class SkillConfidenceSummary(BaseModel):
    """Breakdown of self-reported and profile-based technical readiness."""

    math_comfort: int
    coding_comfort: int
    experience_level: str
    technical_skills_count: int
    programming_languages_count: int
    overall_confidence: int


class AnalyzeInterestRequest(BaseModel):
    """Optional request body to target a specific completed assessment session."""

    session_id: int | None = None


class InterestProfileResponse(BaseModel):
    """Explainable research interest profile returned by the API."""

    id: int
    user_id: int
    session_id: int
    domain_scores: list[ScoreEntry]
    dimension_scores: list[ScoreEntry]
    skill_confidence: SkillConfidenceSummary
    top_domains: list[str]
    limitations_note: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
