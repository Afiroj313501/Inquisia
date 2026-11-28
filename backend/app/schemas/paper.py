from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class PaperItem(BaseModel):
    openalex_id: str
    title: str
    authors: list[str]
    publication_year: int | None
    venue: str | None
    cited_by_count: int
    doi: str | None
    url: str | None
    open_access_url: str | None
    abstract: str | None
    is_saved: bool = False


class PaperSearchResponse(BaseModel):
    source: str
    query: str
    topic_id: str | None
    total_count: int
    results: list[PaperItem]


class SavePaperRequest(BaseModel):
    openalex_id: str = Field(min_length=1, max_length=80)
    topic_id: str | None = Field(default=None, max_length=80)
    title: str = Field(min_length=1)
    authors: list[str] = Field(default_factory=list)
    publication_year: int | None = None
    venue: str | None = Field(default=None, max_length=255)
    cited_by_count: int = Field(default=0, ge=0)
    doi: str | None = Field(default=None, max_length=255)
    url: str | None = None
    open_access_url: str | None = None
    abstract: str | None = None


class SavedPaperResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    openalex_id: str
    topic_id: str | None
    title: str
    authors: list[str]
    publication_year: int | None
    venue: str | None
    cited_by_count: int
    doi: str | None
    url: str | None
    open_access_url: str | None
    abstract: str | None
    created_at: datetime


class LiteratureSynthesisResponse(BaseModel):
    paper_count: int
    paper_titles: list[str]
    model: str
    common_themes: list[str]
    methodological_gaps: list[str]
    next_step_recommendation: str
    ai_generated_notice: str
