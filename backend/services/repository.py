from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.db.models import ResearchSession, ResearchSource, User


def create_user(db: Session, email: str, hashed_password: str) -> User:
    user = User(email=email.lower(), hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(
        select(User).where(User.email == email.lower())
    )


def create_session(db: Session, user_id: str, question: str) -> ResearchSession:
    session = ResearchSession(
        user_id=user_id,
        question=question,
        status="running",
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def complete_session(
    db: Session,
    session: ResearchSession,
    result: dict,
) -> ResearchSession:
    session.status = "completed"
    session.answer = result.get("final_answer")
    session.sub_questions = result.get("sub_questions", [])
    session.contradictions = result.get("contradictions", [])
    session.gaps = result.get("gaps", [])
    session.iterations = result.get("iteration", 0) + 1
    session.completed_at = datetime.now(timezone.utc)

    seen = set()
    for item in result.get("research_results", []):
        key = item.get("url") or f"{item.get('title')}::{item.get('question')}"
        if key in seen:
            continue
        seen.add(key)
        session.sources.append(
            ResearchSource(
                session_id=session.id,
                question=item.get("question", ""),
                title=item.get("title", ""),
                url=item.get("url", ""),
                content=item.get("content", ""),
                score=item.get("score"),
                credibility_label=item.get(
                    "credibility_label", "Unknown"
                ),
                credibility_score=item.get(
                    "credibility_score", 0.3
                ),
            )
        )

    db.commit()
    db.refresh(session)
    return session


def fail_session(db: Session, session: ResearchSession, error: str) -> None:
    session.status = "failed"
    session.error_message = error[:2000]
    session.completed_at = datetime.now(timezone.utc)
    db.commit()


def get_user_session(
    db: Session,
    session_id: str,
    user_id: str,
) -> ResearchSession | None:
    return db.scalar(
        select(ResearchSession).where(
            ResearchSession.id == session_id,
            ResearchSession.user_id == user_id,
        )
    )


def list_user_sessions(
    db: Session,
    user_id: str,
    limit: int = 20,
    offset: int = 0,
) -> list[ResearchSession]:
    return list(
        db.scalars(
            select(ResearchSession)
            .where(ResearchSession.user_id == user_id)
            .order_by(ResearchSession.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
    )
