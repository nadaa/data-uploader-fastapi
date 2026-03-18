from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from typing import AsyncGenerator  
from sqlalchemy.orm import DeclarativeBase

from .config import settings

SQLALCHEMY_DATABASE_URL = f'postgresql+asyncpg://{settings.database_username}:{settings.database_password}@{settings.database_hostname}/{settings.database_name}'


engine = create_async_engine(SQLALCHEMY_DATABASE_URL)


# Create a factory to generate new asynchronous database sessions
asyncSessionLocal = async_sessionmaker(
    engine, 
    expire_on_commit=False,
    class_=AsyncSession,  
    autoflush=False,
)

# Base class for all ORM models
class Base(DeclarativeBase):
    pass


async def init_db():
    """
    Initialize the database and create all tables.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Yield an asynchronous database session and ensure it is closed afterward.
    """
    async with asyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()



