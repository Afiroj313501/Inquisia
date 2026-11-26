from fastapi import HTTPException, status
import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.saved_paper import SavedPaper
from app.schemas.paper import PaperItem, PaperSearchResponse, SavePaperRequest
from app.services.topic_catalog import TOPIC_MAP


def _reconstruct_abstract(inverted_index: dict[str, list[int]] | None) -> str | None:
    if not inverted_index:
        return None
    positions: dict[int, str] = {}
    for word, indices in inverted_index.items():
        for idx in indices:
            positions[idx] = word
    if not positions:
        return None
    return " ".join(positions[i] for i in sorted(positions))


def _map_openalex_work(work: dict[str, object], saved_ids: set[str]) -> PaperItem:
    raw_id = str(work.get("id") or "")
    openalex_id = raw_id.rsplit("/", 1)[-1] if "/" in raw_id else raw_id

    authorships = work.get("authorships")
    authors: list[str] = []
    if isinstance(authorships, list):
        for entry in authorships[:8]:
            if isinstance(entry, dict):
                author = entry.get("author")
                if isinstance(author, dict) and author.get("display_name"):
                    authors.append(str(author["display_name"]))

    primary_loc = work.get("primary_location")
    venue: str | None = None
    landing_url: str | None = None
    if isinstance(primary_loc, dict):
        source = primary_loc.get("source")
        if isinstance(source, dict) and source.get("display_name"):
            venue = str(source["display_name"])
        if primary_loc.get("landing_page_url"):
            landing_url = str(primary_loc["landing_page_url"])

    open_access = work.get("open_access")
    oa_url: str | None = None
    if isinstance(open_access, dict) and open_access.get("oa_url"):
        oa_url = str(open_access["oa_url"])

    doi_val = work.get("doi")
    doi = str(doi_val) if doi_val else None
    url = doi or landing_url or (raw_id or None)

    pub_year_raw = work.get("publication_year")
    pub_year = int(pub_year_raw) if isinstance(pub_year_raw, int) else None

    cited_raw = work.get("cited_by_count")
    cited_by_count = int(cited_raw) if isinstance(cited_raw, int) else 0

    inverted = work.get("abstract_inverted_index")
    abstract = _reconstruct_abstract(inverted if isinstance(inverted, dict) else None)

    title = str(work.get("display_name") or work.get("title") or "Untitled")

    return PaperItem(
        openalex_id=openalex_id,
        title=title,
        authors=authors,
        publication_year=pub_year,
        venue=venue,
        cited_by_count=cited_by_count,
        doi=doi,
        url=url,
        open_access_url=oa_url,
        abstract=abstract,
        is_saved=openalex_id in saved_ids,
    )


def search_papers(
    db: Session,
    user_id: int,
    *,
    topic_id: str | None = None,
    query: str | None = None,
    limit: int = 8,
    sort: str = "relevance",
) -> PaperSearchResponse:
    """Search real peer-reviewed literature via the OpenAlex Works API."""
    search_query: str
    if topic_id:
        topic = TOPIC_MAP.get(topic_id)
        if topic is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Unknown research topic '{topic_id}'.",
            )
        search_query = f"{topic.title} {' '.join(topic.keywords[:3])}".strip()
    elif query and query.strip():
        search_query = query.strip()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide either a topic_id or a non-empty search query.",
        )

    settings = get_settings()
    base_url = settings.openalex_api_base_url.rstrip("/")
    params: dict[str, str | int] = {
        "search": search_query,
        "per-page": limit,
        "filter": "type:article|preprint",
        "sort": "cited_by_count:desc" if sort == "cited_by_count" else "relevance_score:desc",
    }
    if settings.openalex_mailto:
        params["mailto"] = settings.openalex_mailto

    try:
        response = httpx.get(f"{base_url}/works", params=params, timeout=10.0)
        response.raise_for_status()
        payload = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to retrieve literature from OpenAlex right now.",
        ) from exc

    works = payload.get("results")
    if not isinstance(works, list):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unexpected response format from OpenAlex.",
        )

    saved_ids = set(
        db.scalars(select(SavedPaper.openalex_id).where(SavedPaper.user_id == user_id)).all()
    )
    items = [_map_openalex_work(work, saved_ids) for work in works if isinstance(work, dict)]
    meta = payload.get("meta") if isinstance(payload.get("meta"), dict) else {}
    total_count = int(meta.get("count", len(items))) if isinstance(meta, dict) else len(items)

    return PaperSearchResponse(
        source="OpenAlex",
        query=search_query,
        topic_id=topic_id,
        total_count=total_count,
        results=items,
    )


def save_paper(db: Session, user_id: int, payload: SavePaperRequest) -> SavedPaper:
    """Persist a real OpenAlex paper for the authenticated user (idempotent per openalex_id)."""
    existing = db.scalar(
        select(SavedPaper).where(
            SavedPaper.user_id == user_id,
            SavedPaper.openalex_id == payload.openalex_id,
        )
    )
    if existing is not None:
        return existing

    paper = SavedPaper(
        user_id=user_id,
        openalex_id=payload.openalex_id,
        topic_id=payload.topic_id,
        title=payload.title,
        authors=payload.authors,
        publication_year=payload.publication_year,
        venue=payload.venue,
        cited_by_count=payload.cited_by_count,
        doi=payload.doi,
        url=payload.url,
        open_access_url=payload.open_access_url,
        abstract=payload.abstract,
    )
    db.add(paper)
    db.commit()
    db.refresh(paper)
    return paper


def list_saved_papers(db: Session, user_id: int) -> list[SavedPaper]:
    """List all saved papers for the authenticated user, newest first."""
    return list(
        db.scalars(
            select(SavedPaper)
            .where(SavedPaper.user_id == user_id)
            .order_by(SavedPaper.created_at.desc())
        ).all()
    )


def remove_saved_paper(db: Session, user_id: int, saved_paper_id: int) -> None:
    """Delete a saved paper owned by the authenticated user."""
    paper = db.scalar(
        select(SavedPaper).where(
            SavedPaper.id == saved_paper_id,
            SavedPaper.user_id == user_id,
        )
    )
    if paper is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved paper not found.",
        )
    db.delete(paper)
    db.commit()
