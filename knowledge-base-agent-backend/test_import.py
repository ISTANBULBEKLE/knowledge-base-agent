#!/usr/bin/env python3
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    print("Testing imports...")
    from app.api.endpoints import chat
    print("✓ chat imported successfully")
    
    from app.api.endpoints import query
    print("✓ query imported successfully")
    
    from app.api.endpoints import scrape
    print("✓ scrape imported successfully")
    
    from app.api.endpoints import sources
    print("✓ sources imported successfully")
    
    print("\nTesting specific imports from scrape module...")
    from app.services.scraper import WebScraper
    print("✓ WebScraper imported successfully")
    
    from app.services.vector_store import VectorStore
    print("✓ VectorStore imported successfully")
    
    print("\nAll imports successful!")
    
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()