from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine)

from httpx import AsyncClient, ASGITransport # in memory
import os
from sqlalchemy.ext.asyncio import create_async_engine
import pytest_asyncio
import pytest
from sqlalchemy import text
from app.database import get_async_db
from app.main import app
from app.models import Base
from app.config import settings
from app.storage import get_store,STORE_CACHE



# Use sqllite for testing
TEST_DATABASE_URL = f"sqlite+aiosqlite:///./{settings.database_test_name}"

test_engine = create_async_engine(TEST_DATABASE_URL)


TestSessionLocal = async_sessionmaker(
    test_engine,
    expire_on_commit=False,
    class_=AsyncSession)



@pytest_asyncio.fixture()
async def get_test_db_session():
    """
    Provide a new db session per test.
    """
    async with TestSessionLocal() as session:
        yield session
        # rollback all changes after test ends
        await session.rollback()

        

@pytest_asyncio.fixture(autouse=True)
async def override_db_dependency(get_test_db_session):
    """
    Override FastAPI get_async_db dependency with the test session.
    """
    async def override_get_db():
        yield get_test_db_session  # yield the actual session object

    app.dependency_overrides[get_async_db] = override_get_db
    yield
    app.dependency_overrides.clear()


    
@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_test_db():
    """
    Create all tables at the beginning of the test and remove them at the end. 
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(autouse=True)
async def async_test_client():
    """Provide an asynchronous HTTPX test client using an in-memory FastAPI app
       and clean up overrides afterward.
       'autouse=True' makes sure the fixture runs automatically before each test.
    """
    transport = ASGITransport(app=app)  # in-memory ASGI transport
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(autouse=True)
async def clean_files_table(get_test_db_session):
    """
    Ensure files table is empty before each test.
    Prevents data from previous tests leaking in.
    """
    await get_test_db_session.execute(text("DELETE FROM files"))
    await get_test_db_session.commit()



@pytest.fixture(scope="session", autouse=True)
def cleanup_sqlite_db():
    """
    Remove the test SQLite database file after the test session completes.    
    """
    yield  
    if os.path.exists(settings.database_test_name):
        os.remove(settings.database_test_name)



@pytest.fixture(autouse=True)
def patch_upload_root(tmp_path, monkeypatch):
    """
    Patch upload_root to a temporary directory for tests and clear the store cache.
    """
    monkeypatch.setattr(settings, "upload_root", tmp_path)
    STORE_CACHE.clear()  # ensure store rebuilds after patch



@pytest.fixture()
def create_store():
    """
    Return an upload store implementation based on Obstore (e.g., Local, GCS, S3).
    The default store is Local.
    """
    # Clear store cache so local store is rebuilt
    STORE_CACHE.clear()
    return lambda: get_store(settings.default_store_type)