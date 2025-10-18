#!/usr/bin/env python3
"""
Cleanup script to remove orphaned vectors from ChromaDB.
Orphaned vectors are those whose source_id no longer exists in PostgreSQL.

Usage:
    python scripts/cleanup_orphaned_vectors.py
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


async def cleanup_orphaned_vectors():
    """Find and remove vectors whose source_id no longer exists in database"""

    print("=" * 60)
    print("ChromaDB Orphaned Vector Cleanup")
    print("=" * 60)

    # Initialize database connection
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Initialize vector store
    vector_store = VectorStore()

    async with async_session() as session:
        # Get all source IDs from PostgreSQL
        result = await session.execute(select(KnowledgeSource.id))
        valid_source_ids = {str(row[0]) for row in result.all()}

        print(f"\n✓ Found {len(valid_source_ids)} valid sources in PostgreSQL")

        # Get all vectors from ChromaDB
        all_vectors = vector_store.collection.get()

        if not all_vectors or not all_vectors['ids']:
            print("\n✓ No vectors found in ChromaDB")
            return

        total_vectors = len(all_vectors['ids'])
        print(f"✓ Found {total_vectors} total vectors in ChromaDB")

        # Find orphaned vectors
        orphaned_ids = []
        orphaned_by_source = {}

        for i, vector_id in enumerate(all_vectors['ids']):
            metadata = all_vectors['metadatas'][i]
            source_id = metadata.get('source_id')

            if source_id and source_id not in valid_source_ids:
                orphaned_ids.append(vector_id)
                if source_id not in orphaned_by_source:
                    orphaned_by_source[source_id] = []
                orphaned_by_source[source_id].append(vector_id)

        orphaned_count = len(orphaned_ids)

        if orphaned_count == 0:
            print("\n✅ No orphaned vectors found! Database is clean.")
            return

        print(f"\n⚠️  Found {orphaned_count} orphaned vectors from {len(orphaned_by_source)} deleted sources:")
        for source_id, vectors in orphaned_by_source.items():
            print(f"   - Source {source_id}: {len(vectors)} vectors")

        # Ask for confirmation
        print(f"\n🗑️  About to delete {orphaned_count} orphaned vectors")
        response = input("Continue? [y/N]: ")

        if response.lower() != 'y':
            print("\n❌ Cleanup cancelled")
            return

        # Delete orphaned vectors
        print("\n🔄 Deleting orphaned vectors...")
        vector_store.collection.delete(ids=orphaned_ids)

        print(f"\n✅ Successfully deleted {orphaned_count} orphaned vectors")
        print(f"✅ ChromaDB cleaned: {total_vectors - orphaned_count} vectors remaining")

    await engine.dispose()
    print("\n" + "=" * 60)


async def show_stats():
    """Show statistics about current vectors"""

    print("=" * 60)
    print("ChromaDB Vector Store Statistics")
    print("=" * 60)

    # Initialize database connection
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Initialize vector store
    vector_store = VectorStore()

    async with async_session() as session:
        # Get PostgreSQL stats
        result = await session.execute(select(KnowledgeSource))
        sources = result.scalars().all()

        print(f"\n📊 PostgreSQL Sources: {len(sources)}")
        for source in sources:
            print(f"   - {source.title[:50]} (ID: {source.id})")

        # Get ChromaDB stats
        all_vectors = vector_store.collection.get()

        if not all_vectors or not all_vectors['ids']:
            print("\n📊 ChromaDB Vectors: 0")
            print("\n⚠️  No vectors in ChromaDB!")
            await engine.dispose()
            return

        total_vectors = len(all_vectors['ids'])
        vectors_by_source = {}

        for i, vector_id in enumerate(all_vectors['ids']):
            metadata = all_vectors['metadatas'][i]
            source_id = metadata.get('source_id', 'unknown')

            if source_id not in vectors_by_source:
                vectors_by_source[source_id] = 0
            vectors_by_source[source_id] += 1

        print(f"\n📊 ChromaDB Vectors: {total_vectors}")
        print(f"📊 Vectors grouped by source_id:")

        valid_source_ids = {str(s.id) for s in sources}

        for source_id, count in sorted(vectors_by_source.items(), key=lambda x: -x[1]):
            status = "✓" if source_id in valid_source_ids else "⚠️  ORPHANED"
            source_title = next((s.title[:40] for s in sources if str(s.id) == source_id), "Unknown")
            print(f"   {status} {source_id}: {count} vectors ({source_title})")

    await engine.dispose()
    print("\n" + "=" * 60)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="ChromaDB Vector Cleanup Utility")
    parser.add_argument("--stats", action="store_true", help="Show statistics only")
    parser.add_argument("--cleanup", action="store_true", help="Cleanup orphaned vectors")

    args = parser.parse_args()

    if args.stats:
        asyncio.run(show_stats())
    elif args.cleanup:
        asyncio.run(cleanup_orphaned_vectors())
    else:
        print("Usage:")
        print("  python scripts/cleanup_orphaned_vectors.py --stats    # Show statistics")
        print("  python scripts/cleanup_orphaned_vectors.py --cleanup  # Clean orphaned vectors")
