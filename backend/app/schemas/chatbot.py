"""Chatbot request/response schemas."""
from typing import Literal, Optional

from pydantic import BaseModel, Field

from app.schemas.common import Lang


class ChatQueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    lang: Lang = "en"


class ChatSource(BaseModel):
    """Retrieved chunk reference — surfaced only in admin/debug mode."""

    source_type: str
    source_id: int
    score: float


class ChatQueryResponse(BaseModel):
    answer: str
    # All 5 statuses that build_question_answer() can return
    status: Literal[
        "answered",
        "unrelated",
        "no_answer",
        "error",
        "needs_clarification"
    ] = "answered"
    # Populated only for 'answered' responses; frontend should hide this from
    # end users and surface it in admin/debug mode only (spec section 10).
    sources: Optional[list[ChatSource]] = None
