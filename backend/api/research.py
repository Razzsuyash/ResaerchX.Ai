import json
import logging
from collections.abc import Generator
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.agent.graph import research_graph
from backend.agent.state import ResearchState
from backend.core.config import settings
from backend.db.database import SessionLocal, get_db
from backend.db.models import User
from backend.models.schemas import HistoryItem, ResearchRequest, ResearchResponse
from backend.services.auth import get_current_user
from backend.core.rate_limit import limiter
from backend.services.repository import (
    complete_session,
    create_session,
    fail_session,
    get_user_session,
    list_user_sessions,
)


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/research", tags=["Research"])


def initial_state(question: str) -> ResearchState:
    return {
        "question": question,
        "sub_questions": [],
        "research_results": [],
        "contradictions": [],
        "gaps": [],
        "iteration": 0,
        "final_answer": "",
    }


def session_to_response(session):
    return ResearchResponse(
        id=session.id,
        question=session.question,
        status=session.status,
        answer=session.answer,
        sub_questions=session.sub_questions or [],
        sources=session.sources,
        contradictions=session.contradictions or [],
        gaps=session.gaps or [],
        iterations=session.iterations,
        created_at=session.created_at,
        completed_at=session.completed_at,
    )


@router.post("", response_model=ResearchResponse)
@limiter.limit(settings.rate_limit_research)
def create_research(
    request: Request,
    body: ResearchRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    session = create_session(db, user.id, body.question)

    try:
        result = research_graph.invoke(
            initial_state(body.question),
            {"recursion_limit": settings.graph_recursion_limit},
        )
        complete_session(db, session, result)
        return session_to_response(session)
    except Exception as exc:
        logger.exception("research_failed session_id=%s", session.id)
        fail_session(db, session, str(exc))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Research service temporarily unavailable.",
        ) from exc


def sse(event: str, data: dict) -> str:
    payload = json.dumps(data, ensure_ascii=False)
    return f"event: {event}\ndata: {payload}\n\n"


@router.post("/stream")
@limiter.limit(settings.rate_limit_research)
def stream_research(
    request: Request,
    body: ResearchRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    session = create_session(db, user.id, body.question)
    session_id = session.id

    def generate() -> Generator[str, None, None]:
        stream_db = SessionLocal()
        stream_session = stream_db.get(type(session), session_id)

        yield sse(
            "started",
            {
                "session_id": session_id,
                "message": "Research started",
            },
        )

        final_state = initial_state(body.question)

        try:
            for chunk in research_graph.stream(
                final_state,
                {"recursion_limit": settings.graph_recursion_limit},
                stream_mode=["updates", "values"],
                version="v2",
            ):
                if chunk["type"] == "updates":
                    for node_name, update in chunk["data"].items():
                        yield sse(
                            "progress",
                            {
                                "session_id": session_id,
                                "node": node_name,
                                "status": "completed",
                                "details": {
                                    key: (
                                        len(value)
                                        if isinstance(value, list)
                                        else value
                                    )
                                    for key, value in update.items()
                                    if key not in {"research_results"}
                                },
                            },
                        )

                elif chunk["type"] == "values":
                    final_state = chunk["data"]

            complete_session(stream_db, stream_session, final_state)

            yield sse(
                "completed",
                {
                    "session_id": session_id,
                    "status": "completed",
                    "answer": stream_session.answer,
                    "sub_questions": stream_session.sub_questions or [],
                    "contradictions": stream_session.contradictions or [],
                    "gaps": stream_session.gaps or [],
                    "iterations": stream_session.iterations,
                    "source_count": len(stream_session.sources),
                },
            )

        except Exception as exc:
            logger.exception("stream_research_failed session_id=%s", session_id)
            if stream_session is not None:
                fail_session(stream_db, stream_session, str(exc))
            yield sse(
                "error",
                {
                    "session_id": session_id,
                    "status": "failed",
                    "message": "Research service temporarily unavailable.",
                },
            )
        finally:
            stream_db.close()

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/{session_id}", response_model=ResearchResponse)
def get_research(
    session_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    session = get_user_session(db, session_id, user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Research session not found.")
    return session_to_response(session)


@router.get("", response_model=list[HistoryItem])
def get_history(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    limit = min(max(limit, 1), 100)
    offset = max(offset, 0)
    return list_user_sessions(db, user.id, limit, offset)


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_research(
    session_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    session = get_user_session(db, session_id, user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Research session not found.")
    db.delete(session)
    db.commit()
    return None
