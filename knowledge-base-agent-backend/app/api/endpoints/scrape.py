from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.models.source import KnowledgeSource
from app.services.scraper import WebScraper
from app.services.vector_store import VectorStore

router = APIRouter()

class ScrapeRequest(BaseModel):
    url: str

@router.post("/scrape")
async def scrape_url(
    request: ScrapeRequest,
    db: AsyncSession = Depends(get_db)
):
    """Scrape a URL and add to knowledge base"""
    
    # Check if URL already exists
    result = await db.execute(
        select(KnowledgeSource).where(KnowledgeSource.url == request.url)
    )
    existing_source = result.scalar_one_or_none()
    
    if existing_source:
        return {"message": "URL already exists in knowledge base", "source_id": str(existing_source.id)}
    
    # Create new source entry
    source = KnowledgeSource(
        url=request.url,
        status="processing"
    )
    db.add(source)
    await db.commit()
    await db.refresh(source)
    
    try:
        # Scrape the URL
        scraper = WebScraper()
        scraped_data = await scraper.scrape_url(request.url)
        
        # Update source with scraped data
        source.title = scraped_data.get("title", "")
        source.content = scraped_data.get("content", "")
        source.source_metadata = scraped_data.get("metadata", {})
        source.status = scraped_data.get("status", "completed")
        source.scraped_at = datetime.utcnow()
        
        # Add to vector store if successful
        if scraped_data.get("status") == "completed" and scraped_data.get("content"):
            vector_store = VectorStore()
            await vector_store.add_document(
                scraped_data["content"],
                {
                    "url": request.url,
                    "title": scraped_data.get("title", ""),
                    "source_id": str(source.id)
                }
            )
        
        await db.commit()
        
        return {
            "message": "URL scraped successfully",
            "source_id": str(source.id),
            "title": source.title,
            "status": source.status
        }
        
    except Exception as e:
        # Update source with error status
        source.status = "error"
        source.source_metadata = {"error": str(e)}
        await db.commit()
        
        raise HTTPException(status_code=500, detail=f"Failed to scrape URL: {str(e)}")