from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime
import uuid

class ChatSessionCreate(BaseModel):
    title: str

class ChatSessionResponse(BaseModel):
    id: uuid.UUID
    title: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ChatMessageResponse(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    content: str
    role: str
    sources: Optional[List[Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True