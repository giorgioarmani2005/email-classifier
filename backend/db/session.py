from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from db.config import settings
from typing import AsyncGenerator

engine = create_async_engine(settings.get_postgres_url(), echo=False)

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
