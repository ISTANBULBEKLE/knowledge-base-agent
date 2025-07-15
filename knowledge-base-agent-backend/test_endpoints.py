#!/usr/bin/env python3
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    print("Testing endpoint routes...")
    
    from app.api.endpoints.scrape import router as scrape_router
    print(f"✓ scrape router has {len(scrape_router.routes)} routes")
    for route in scrape_router.routes:
        print(f"  - {route.methods} {route.path}")
    
    from app.api.endpoints.sources import router as sources_router
    print(f"✓ sources router has {len(sources_router.routes)} routes")
    for route in sources_router.routes:
        print(f"  - {route.methods} {route.path}")
    
    print("\nEndpoints look good!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()