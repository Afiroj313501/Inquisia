from datetime import datetime, timezone
from typing import Any
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.assessment import AssessmentResponse, AssessmentSession
from app.schemas.assessment import (
    AssessmentProgressSchema,
    AssessmentSessionDetail,
    QuestionOptionSchema,
    QuestionSchema,
)
from app.services.question_bank import (
    QUESTION_MAP,
    QuestionDefinition,
    resolve_applicable_questions,
    validate_answer_for_question,
)


def _serialize_question(q: QuestionDefinition) -> QuestionSchema:
    return QuestionSchema(
        id=q.id,
        prompt=q.prompt,
        question_type=q.question_type,
        category=q.category,
        help_text=q.help_text,
        options=[
            QuestionOptionSchema(id=opt.id, label=opt.label, description=opt.description)
            for opt in q.options
        ],
        min_value=q.min_value,
        max_value=q.max_value,
        min_label=q.min_label,
        max_label=q.max_label,
        max_selections=q.max_selections,
        is_adaptive=q.is_adaptive,
    )


def build_session_detail(session: AssessmentSession) -> AssessmentSessionDetail:
    """Resolve applicable questions and progress metrics for a session."""
    all_answers = {resp.question_id: resp.answer_value for resp in session.responses}
    applicable_questions = resolve_applicable_questions(all_answers)
    applicable_ids = {q.id for q in applicable_questions}

    active_answers = {
        qid: val for qid, val in all_answers.items() if qid in applicable_ids
    }

    next_question_id = next(
        (q.id for q in applicable_questions if q.id not in active_answers),
        None,
    )

    total = len(applicable_questions)
    answered = len(active_answers)
    percent = round((answered / total) * 100) if total > 0 else 0

    return AssessmentSessionDetail(
        id=session.id,
        status=session.status,  # type: ignore[arg-type]
        current_question_id=session.current_question_id or next_question_id,
        started_at=session.started_at,
        updated_at=session.updated_at,
        completed_at=session.completed_at,
        questions=[_serialize_question(q) for q in applicable_questions],
        responses=active_answers,
        progress=AssessmentProgressSchema(
            answered_count=answered,
            total_questions=total,
            progress_percent=percent,
            next_question_id=next_question_id,
        ),
    )


def _load_session(db: Session, session_id: int) -> AssessmentSession | None:
    stmt = (
        select(AssessmentSession)
        .options(selectinload(AssessmentSession.responses))
        .where(AssessmentSession.id == session_id)
    )
    return db.scalar(stmt)


def get_session_for_user(
    db: Session, session_id: int, user_id: int
) -> AssessmentSession:
    """Load an assessment session owned by the user or raise 404."""
    session = _load_session(db, session_id)
    if session is None or session.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment session not found.",
        )
    return session


def get_latest_session_for_user(
    db: Session, user_id: int
) -> AssessmentSession | None:
    """Return the user's most recent assessment session, if any."""
    stmt = (
        select(AssessmentSession)
        .options(selectinload(AssessmentSession.responses))
        .where(AssessmentSession.user_id == user_id)
        .order_by(AssessmentSession.id.desc())
        .limit(1)
    )
    return db.scalar(stmt)


def start_or_resume_session(
    db: Session, user_id: int, resume_if_active: bool = True
) -> AssessmentSession:
    """Resume an in-progress session if requested, or create a new session."""
    if resume_if_active:
        stmt = (
            select(AssessmentSession)
            .options(selectinload(AssessmentSession.responses))
            .where(
                AssessmentSession.user_id == user_id,
                AssessmentSession.status == "in_progress",
            )
            .order_by(AssessmentSession.id.desc())
            .limit(1)
        )
        existing = db.scalar(stmt)
        if existing is not None:
            return existing

    first_question_id = resolve_applicable_questions({})[0].id
    session = AssessmentSession(
        user_id=user_id,
        status="in_progress",
        current_question_id=first_question_id,
    )
    db.add(session)
    db.commit()
    return get_session_for_user(db, session.id, user_id)


def save_response(
    db: Session,
    session_id: int,
    user_id: int,
    question_id: str,
    answer_value: Any,
    current_question_id: str | None = None,
) -> AssessmentSession:
    """Validate and save/update a question response in an in-progress session."""
    session = get_session_for_user(db, session_id, user_id)
    if session.status == "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Completed assessment sessions cannot be modified.",
        )

    question = QUESTION_MAP.get(question_id)
    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown question '{question_id}'.",
        )

    existing_answers = {r.question_id: r.answer_value for r in session.responses}
    applicable_ids = {q.id for q in resolve_applicable_questions(existing_answers)}
    if question_id not in applicable_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Question '{question_id}' is not currently unlocked for this session.",
        )

    try:
        normalized_answer = validate_answer_for_question(question, answer_value)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    existing_row = next(
        (r for r in session.responses if r.question_id == question_id),
        None,
    )
    if existing_row is not None:
        existing_row.answer_value = normalized_answer
    else:
        db.add(
            AssessmentResponse(
                session_id=session.id,
                question_id=question_id,
                answer_value=normalized_answer,
            )
        )

    if current_question_id is not None:
        session.current_question_id = current_question_id
    else:
        updated_answers = {**existing_answers, question_id: normalized_answer}
        updated_questions = resolve_applicable_questions(updated_answers)
        next_q = next(
            (q.id for q in updated_questions if q.id not in updated_answers),
            question_id,
        )
        session.current_question_id = next_q

    db.commit()
    return get_session_for_user(db, session.id, user_id)


def complete_session(
    db: Session, session_id: int, user_id: int
) -> AssessmentSession:
    """Mark an assessment session completed once all applicable questions are answered."""
    session = get_session_for_user(db, session_id, user_id)
    if session.status == "completed":
        return session

    detail = build_session_detail(session)
    if detail.progress.answered_count < detail.progress.total_questions:
        missing = [
            q.id for q in detail.questions if q.id not in detail.responses
        ]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Please answer all required questions before completing ({len(missing)} remaining).",
        )

    session.status = "completed"
    session.completed_at = datetime.now(timezone.utc)
    db.commit()
    return get_session_for_user(db, session.id, user_id)
