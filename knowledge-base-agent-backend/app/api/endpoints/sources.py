from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid

from app.core.database import get_db
from app.models.source import KnowledgeSource

router = APIRouter()

class SourceResponse(BaseModel):
    id: uuid.UUID
    url: str
    title: str
    description: Optional[str] = None
    status: str
    scraped_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

@router.get("/sources", response_model=List[SourceResponse])
async def get_sources(
    limit: int = 50,
    status: str = None,
    db: AsyncSession = Depends(get_db)
):
    """Get knowledge sources"""
    query = select(KnowledgeSource).order_by(desc(KnowledgeSource.created_at))
    
    if status:
        query = query.where(KnowledgeSource.status == status)
    
    query = query.limit(limit)
    result = await db.execute(query)
    sources = result.scalars().all()
    
    return [
        SourceResponse(
            id=source.id,
            url=source.url,
            title=source.title or "",
            description=source.description,
            status=source.status,
            scraped_at=source.scraped_at,
            created_at=source.created_at
        )
        for source in sources
    ]