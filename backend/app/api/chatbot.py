"""Chatbot API skeleton.

Phase 2 provides the endpoint contract. The relevance gate, retrieval, and
answer generation land in Phase 4 (RAG) and Phase 8 (Chatbot integration).
"""
from fastapi import APIRouter

from app.schemas.chatbot import ChatQueryRequest, ChatQueryResponse

router = APIRouter(tags=["chatbot"])


@router.post("/query", response_model=ChatQueryResponse)
async def query(payload: ChatQueryRequest) -> ChatQueryResponse:
    # Full decision flow (relevance gate -> retrieval -> generation -> fallbacks)
    # is implemented in Phase 4 + Phase 8.
    return ChatQueryResponse(
        answer=(
            "Chatbot is not active yet — RAG and generation are implemented in "
            "later phases."
        ),
        status="no_answer",
    )
