#!/usr/bin/env python3
"""
Re-index existing sources in ChromaDB.
Useful after ChromaDB has been reset or for sources that failed to vectorize.

Usage:
    python scripts/reindex_sources.py
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.source import KnowledgeSource
from app.services.vector_store import VectorStore


async def reindex_all_sources():
    """Re-index all completed sources in the vector store"""

    print("=" * 60)
    print("ChromaDB Source Re-indexing")
    print("=" * 60)

    # Initialize database connection
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Initialize vector store
    vector_store = VectorStore()

    # Get current vectors
    existing_vectors = vector_store.collection.get()
    existing_source_ids = set()
    if existing_vectors and existing_vectors['metadatas']:
        for metadata in existing_vectors['metadatas']:
            source_id = metadata.get('source_id')
            if source_id:
                existing_source_ids.add(source_id)

    print(f"\n✓ Found {len(existing_source_ids)} sources already in ChromaDB")

    async with async_session() as session:
        # Get all completed sources
        result = await session.execute(
            select(KnowledgeSource)
            .where(KnowledgeSource.status == "completed")
            .order_by(KnowledgeSource.created_at.desc())
        )
        sources = result.scalars().all()

        print(f"✓ Found {len(sources)} completed sources in PostgreSQL\n")

        reindexed = 0
        skipped = 0
        failed = 0

        for source in sources:
            source_id = str(source.id)

            # Check if source already has vectors
            if source_id in existing_source_ids:
                print(f"⊘ Skipping: {source.title[:50]} (already indexed)")
                skipped += 1
                continue

            # Check if source has content
            if not source.content or len(source.content.strip()) == 0:
                print(f"✗ Skipping: {source.title[:50]} (no content)")
                failed += 1
                continue

            try:
                print(f"⟳ Indexing: {source.title[:50]}...")
                print(f"  Content length: {len(source.content)} characters")

                # Add to vector store
                metadata = {
                    "source_id": source_id,
                    "title": source.title or "Untitled",
                    "url": source.url,
                    "source_type": "document_upload" if source.url.startswith("file://") else "web_scrape"
                }

                doc_id = await vector_store.add_document(
                    content=source.content,
                    metadata=metadata
                )

                print(f"  ✓ Successfully indexed with doc_id: {doc_id}")
                reindexed += 1

            except Exception as e:
                print(f"  ✗ Failed to index: {str(e)}")
                failed += 1

        print("\n" + "=" * 60)
        print("Re-indexing Summary")
        print("=" * 60)
        print(f"✓ Successfully re-indexed: {reindexed}")
        print(f"⊘ Already indexed (skipped): {skipped}")
        print(f"✗ Failed: {failed}")
        print(f"📊 Total in ChromaDB: {len(existing_source_ids) + reindexed}")
        print("=" * 60)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(reindex_all_sources())
