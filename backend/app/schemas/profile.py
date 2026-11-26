from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

EducationLevel = Literal[
    "high_school",
    "undergraduate",
    "masters",
    "phd",
    "postdoc",
    "industry",
    "other",
]

ResearchExperienceLevel = Literal[
    "none",
    "beginner",
    "intermediate",
    "experienced",
]


def _normalize_tag_list(items: list[str]) -> list[str]:
    """Strip whitespace, drop empty entries, and deduplicate case-insensitively."""
    seen: set[str] = set()
    normalized: list[str] = []
    for raw in items:
        cleaned = raw.strip()
        if not cleaned:
            continue
        key = cleaned.lower()
        if key not in seen:
            seen.add(key)
            normalized.append(cleaned)
    return normalized


class AcademicProfileUpsert(BaseModel):
    """Payload for creating or updating the authenticated user's academic profile."""

    education_level: EducationLevel
    degree_program: str = Field(min_length=2, max_length=160)
    academic_background: str | None = Field(default=None, max_length=2000)
    technical_skills: list[str] = Field(default_factory=list, max_length=50)
    programming_languages: list[str] = Field(default_factory=list, max_length=30)
    preferred_research_domains: list[str] = Field(default_factory=list, max_length=30)
    research_experience_level: ResearchExperienceLevel
    research_experience_summary: str | None = Field(default=None, max_length=2000)
    career_goals: str | None = Field(default=None, max_length=2000)
    weekly_hours_available: int | None = Field(default=None, ge=1, le=80)

    @field_validator(
        "technical_skills",
        "programming_languages",
        "preferred_research_domains",
        mode="after",
    )
    @classmethod
    def normalize_lists(cls, value: list[str]) -> list[str]:
        return _normalize_tag_list(value)

    @field_validator("degree_program", mode="after")
    @classmethod
    def strip_degree_program(cls, value: str) -> str:
        cleaned = value.strip()
        if len(cleaned) < 2:
            raise ValueError("Degree program must be at least 2 characters.")
        return cleaned


class AcademicProfileResponse(BaseModel):
    """Serialized academic profile returned by the API."""

    id: int
    user_id: int
    education_level: EducationLevel
    degree_program: str
    academic_background: str | None
    technical_skills: list[str]
    programming_languages: list[str]
    preferred_research_domains: list[str]
    research_experience_level: ResearchExperienceLevel
    research_experience_summary: str | None
    career_goals: str | None
    weekly_hours_available: int | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
