"""Chatbot request/response schemas."""
from typing import Optional

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
    # 'answered' | 'unrelated' | 'no_answer' | 'error'
    status: str = "answered"
    sources: Optional[list[ChatSource]] = None
