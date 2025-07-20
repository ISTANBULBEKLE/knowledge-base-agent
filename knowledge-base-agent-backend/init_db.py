import asyncio
from app.core.database import async_engine
from app.models.source import Base
from app.models import chat  # Import chat models to register them

async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created successfully!")

if __name__ == "__main__":
    asyncio.run(init_db())