from typing import Literal
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.paper import (
    LiteratureSynthesisResponse,
    PaperSearchResponse,
    SavePaperRequest,
    SavedPaperResponse,
)
from app.services.brief_service import synthesize_saved_papers
from app.services.paper_service import (
    list_saved_papers,
    remove_saved_paper,
    save_paper,
    search_papers,
)

router = APIRouter(prefix="/papers", tags=["papers"])


@router.get("/search", response_model=PaperSearchResponse)
def search_academic_papers(
    topic_id: str | None = Query(default=None),
    query: str | None = Query(default=None),
    limit: int = Query(default=8, ge=1, le=20),
    sort: Literal["relevance", "cited_by_count"] = Query(default="relevance"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PaperSearchResponse:
    """Search real academic papers from OpenAlex for a recommended topic or custom query."""
    return search_papers(
        db,
        current_user.id,
        topic_id=topic_id,
        query=query,
        limit=limit,
        sort=sort,
    )


@router.get("/saved", response_model=list[SavedPaperResponse])
def read_saved_papers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[SavedPaperResponse]:
    """List all academic papers saved by the authenticated user."""
    papers = list_saved_papers(db, current_user.id)
    return [SavedPaperResponse.model_validate(paper) for paper in papers]


@router.post(
    "/saved",
    response_model=SavedPaperResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_saved_paper(
    payload: SavePaperRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SavedPaperResponse:
    """Save a real academic paper to the user's research workspace."""
    paper = save_paper(db, current_user.id, payload)
    return SavedPaperResponse.model_validate(paper)


@router.delete("/saved/{saved_paper_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_saved_paper(
    saved_paper_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Remove a saved academic paper from the user's workspace."""
    remove_saved_paper(db, current_user.id, saved_paper_id)


@router.post("/synthesize", response_model=LiteratureSynthesisResponse)
def synthesize_literature(
    topic_id: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> LiteratureSynthesisResponse:
    """Synthesize common themes and gaps across the user's saved OpenAlex papers."""
    return synthesize_saved_papers(db, current_user.id, topic_id=topic_id)
