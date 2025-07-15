#!/usr/bin/env python3
import sys
import asyncio
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

async def test_sources_endpoint():
    try:
        print("Testing sources endpoint directly...")
        
        from app.api.endpoints.sources import get_sources
        from app.core.database import get_db
        
        # Get database session
        db_gen = get_db()
        db = await db_gen.__anext__()
        
        # Call the endpoint function directly
        result = await get_sources(db=db)
        print(f"✓ Sources endpoint returned: {result}")
        
        await db.close()
        
    except Exception as e:
        print(f"❌ Error in sources endpoint: {e}")
        import traceback
        traceback.print_exc()

async def test_scrape_endpoint():
    try:
        print("\nTesting scrape endpoint directly...")
        
        from app.api.endpoints.scrape import scrape_url, ScrapeRequest
        from app.core.database import get_db
        
        # Get database session
        db_gen = get_db()
        db = await db_gen.__anext__()
        
        # Create request
        request = ScrapeRequest(url="https://httpbin.org/json")
        
        # Call the endpoint function directly
        result = await scrape_url(request=request, db=db)
        print(f"✓ Scrape endpoint returned: {result}")
        
        await db.close()
        
    except Exception as e:
        print(f"❌ Error in scrape endpoint: {e}")
        import traceback
        traceback.print_exc()

async def main():
    await test_sources_endpoint()
    await test_scrape_endpoint()

if __name__ == "__main__":
    asyncio.run(main())