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

@router.delete("/sources/{source_id}")
async def delete_source(
    source_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete a knowledge source"""
    try:
        # Find the source
        result = await db.execute(
            select(KnowledgeSource).where(KnowledgeSource.id == str(source_id))
        )
        source = result.scalar_one_or_none()

        if not source:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Source not found")

        # Delete from database
        await db.delete(source)
        await db.commit()

        # Note: Vector embeddings in ChromaDB are not automatically deleted
        # You may want to implement ChromaDB cleanup based on source_id metadata

        return {
            "message": "Source deleted successfully",
            "source_id": str(source_id)
        }

    except Exception as e:
        await db.rollback()
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Error deleting source: {str(e)}")