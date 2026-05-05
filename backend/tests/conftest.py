"""
Test configuration.

Uses an in-memory SQLite database so tests run without a Postgres instance.
Face detection tests use mocks or synthetic Pillow images.
"""
import contextlib
import io
import os
import pytest
import pytest_asyncio
import httpx
from httpx import ASGITransport, AsyncClient
from httpx_ws import aconnect_ws
from httpx_ws.transport import ASGIWebSocketTransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

from app.database import Base, get_db_session  # noqa: E402
from app.main import create_app  # noqa: E402

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="session")
async def engine():
    eng = create_async_engine(TEST_DB_URL, echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture
async def db_session(engine):
    factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(engine):
    factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async def override_db():
        async with factory() as session:
            yield session

    app = create_app()
    app.dependency_overrides[get_db_session] = override_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as ac:
        yield ac


@pytest.fixture
def ws_app(engine):
    """Return a FastAPI app wired to the test SQLite engine, ready for WS testing.

    ASGIWebSocketTransport does not run the FastAPI lifespan, so we seed
    app.state manually here (mirrors what lifespan() does at startup).
    """
    factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async def override_db():
        async with factory() as session:
            yield session

    app = create_app()
    app.dependency_overrides[get_db_session] = override_db
    app.state.queue_registry = {}
    app.state.frame_counters = {}
    return app


@pytest.fixture
def blank_jpeg() -> bytes:
    """A 100x100 white JPEG — no face."""
    from PIL import Image
    img = Image.new("RGB", (100, 100), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


@pytest.fixture
def noise_jpeg() -> bytes:
    """Random noise JPEG — definitely no face."""
    import numpy as np
    from PIL import Image
    arr = np.random.randint(0, 256, (120, 120, 3), dtype=np.uint8)
    img = Image.fromarray(arr)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()
