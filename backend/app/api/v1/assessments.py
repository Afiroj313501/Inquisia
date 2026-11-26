from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.assessment import (
    AssessmentSessionDetail,
    SaveResponseRequest,
    StartSessionRequest,
)
from app.services.assessment_service import (
    build_session_detail,
    complete_session,
    get_latest_session_for_user,
    get_session_for_user,
    save_response,
    start_or_resume_session,
)

router = APIRouter(prefix="/assessments", tags=["assessments"])


@router.post("/sessions", response_model=AssessmentSessionDetail)
def start_assessment_session(
    payload: StartSessionRequest | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AssessmentSessionDetail:
    """Start a new assessment session or resume an active one."""
    resume = payload.resume_if_active if payload is not None else True
    session = start_or_resume_session(db, current_user.id, resume_if_active=resume)
    return build_session_detail(session)


@router.get("/sessions/latest", response_model=AssessmentSessionDetail)
def read_latest_assessment_session(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AssessmentSessionDetail:
    """Return the authenticated user's most recent assessment session."""
    session = get_latest_session_for_user(db, current_user.id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No assessment session found.",
        )
    return build_session_detail(session)


@router.get("/sessions/{session_id}", response_model=AssessmentSessionDetail)
def read_assessment_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AssessmentSessionDetail:
    """Return a specific assessment session owned by the authenticated user."""
    session = get_session_for_user(db, session_id, current_user.id)
    return build_session_detail(session)


@router.put("/sessions/{session_id}/responses", response_model=AssessmentSessionDetail)
def upsert_assessment_response(
    session_id: int,
    payload: SaveResponseRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AssessmentSessionDetail:
    """Save or update an answer for a question and recompute adaptive follow-ups."""
    session = save_response(
        db=db,
        session_id=session_id,
        user_id=current_user.id,
        question_id=payload.question_id,
        answer_value=payload.answer_value,
        current_question_id=payload.current_question_id,
    )
    return build_session_detail(session)


@router.post("/sessions/{session_id}/complete", response_model=AssessmentSessionDetail)
def complete_assessment_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AssessmentSessionDetail:
    """Complete an assessment session after all applicable questions are answered."""
    session = complete_session(db, session_id, current_user.id)
    return build_session_detail(session)
