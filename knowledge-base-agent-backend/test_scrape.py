#!/usr/bin/env python3
import asyncio
import os
import sys
from pathlib import Path
import time

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import get_db
from app.models.source import KnowledgeSource
from app.services.scraper import WebScraper
from sqlalchemy.ext.asyncio import AsyncSession

async def test_scrape():
    try:
        print("Testing scraper...")
        scraper = WebScraper()
        result = await scraper.scrape_url('https://httpbin.org/json')
        print(f"Scraper result: {result}")
        
        print("\nTesting database connection...")
        # Get database session
        db_gen = get_db()
        db = await db_gen.__anext__()
        print("Database connection successful")
        
        # Test creating a source with unique URL
        timestamp = int(time.time())
        source = KnowledgeSource(
            url=f"https://test-{timestamp}.com",
            title="Test",
            status="pending"
        )
        db.add(source)
        await db.commit()
        print(f"Created source: {source.id}")
        
        await db.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_scrape())