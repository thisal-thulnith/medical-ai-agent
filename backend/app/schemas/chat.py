from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.conversation import MessageRole


class ChatMessage(BaseModel):
    role: MessageRole
    content: str
    timestamp: Optional[datetime] = None
    meta_data: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
        # Explicitly ignore SQLAlchemy's metadata attribute
        ignored_types = (type(None),)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    conversation_id: Optional[int] = None
    include_history: bool = True


class ChatResponse(BaseModel):
    conversation_id: int
    message: ChatMessage
    extracted_data: Optional[Dict[str, Any]] = None  # Health data extracted from conversation


class ConversationResponse(BaseModel):
    id: int
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    message_count: int
    last_message: Optional[str] = None

    class Config:
        from_attributes = True


class ConversationDetail(BaseModel):
    id: int
    title: Optional[str]
    created_at: datetime
    messages: List[ChatMessage]

    class Config:
        from_attributes = True
