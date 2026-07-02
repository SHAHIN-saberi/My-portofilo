"""Chatbot API — wired to the RAG decision flow.

Endpoint contract only; all decisioning (scope filter, relevance gate,
retrieval, rerank, generation, fallbacks, stop conditions, clarification)
lives in `app.services.rag`.
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.limiter import limiter
from app.db.session import get_db
from app.schemas.chatbot import ChatQueryRequest, ChatQueryResponse, ChatSource
from app.services.ai_provider.base import AIProvider
from app.services.ai_provider.factory import get_ai_provider
from app.services.rag import FALLBACK_ERROR, build_question_answer

router = APIRouter(tags=["chatbot"])


@router.post("/query", response_model=ChatQueryResponse)
@limiter.limit("20/minute")
async def query(
    request: Request,
    payload: ChatQueryRequest,
    session: AsyncSession = Depends(get_db),
    ai_provider: AIProvider = Depends(get_ai_provider),
    settings: Settings = Depends(get_settings),
) -> ChatQueryResponse:
    try:
        result = await build_question_answer(
            session=session,
            ai_provider=ai_provider,
            question=payload.question,
            lang=payload.lang,
            top_k=settings.rag_top_k,
            similarity_threshold=settings.rag_similarity_threshold,
        )
    except Exception:
        # Any unexpected failure degrades to the same polite fallback the
        # spec mandates for provider/embedding failures -- never a 500 that
        # exposes internals to a visitor.
        return ChatQueryResponse(answer=FALLBACK_ERROR, status="error", sources=None)

    sources = None
    if result["status"] == "answered" and result.get("sources"):
        sources = [ChatSource(**src) for src in result["sources"]]

    return ChatQueryResponse(
        answer=result["answer"],
        status=result["status"],
        sources=sources,
    )
