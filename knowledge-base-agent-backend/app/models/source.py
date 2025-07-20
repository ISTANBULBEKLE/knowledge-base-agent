from sqlalchemy import Column, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class KnowledgeSource(Base):
    __tablename__ = "knowledge_sources"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    url = Column(Text, unique=True, nullable=False)
    title = Column(String(500))
    description = Column(Text)
    content = Column(Text)
    source_metadata = Column(JSON)
    status = Column(String(20), default="pending")  # pending, processing, completed, error
    scraped_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())