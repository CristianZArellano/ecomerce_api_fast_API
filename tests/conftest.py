"""
Shared pytest fixtures for the E-commerce API tests.
"""

import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Import your app and dependencies
from app.config import get_settings
from app.database import Base, get_database
from app.models import Product, User
from main import app


# Test database configuration
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
TEST_DATABASE_URL_SYNC = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def async_engine():
    """Create async test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()


@pytest.fixture
async def async_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create async test database session."""
    async_session_maker = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session_maker() as session:
        yield session


@pytest.fixture
def sync_engine():
    """Create sync test database engine."""
    engine = create_engine(
        TEST_DATABASE_URL_SYNC,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    
    Base.metadata.create_all(engine)
    yield engine
    
    engine.dispose()


@pytest.fixture
def sync_session(sync_engine) -> Generator[Session, None, None]:
    """Create sync test database session."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=sync_engine
    )
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def override_get_db(async_session: AsyncSession):
    """Override database dependency for testing."""
    async def _override_get_db():
        yield async_session
    
    return _override_get_db


@pytest.fixture
def test_app(override_get_db):
    """Create FastAPI test application."""
    app.dependency_overrides[get_database] = override_get_db
    yield app
    app.dependency_overrides.clear()


@pytest.fixture
def client(test_app) -> Generator[TestClient, None, None]:
    """Create test client for sync testing."""
    with TestClient(test_app) as test_client:
        yield test_client


@pytest.fixture
async def async_client(test_app) -> AsyncGenerator[AsyncClient, None]:
    """Create async test client."""
    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://testserver"
    ) as ac:
        yield ac


@pytest.fixture
async def test_user(async_session: AsyncSession) -> User:
    """Create a test user."""
    from app.crud import create_user
    from app.schemas import UserCreate
    
    user_data = UserCreate(
        name="Test User",
        email="test@example.com",
        password="testpassword123"
    )
    user = await create_user(async_session, user_data)
    await async_session.commit()
    await async_session.refresh(user)
    return user


@pytest.fixture
async def admin_user(async_session: AsyncSession) -> User:
    """Create a test admin user."""
    from app.crud import create_user
    from app.schemas import UserCreate
    
    user_data = UserCreate(
        name="Admin User",
        email="admin@example.com",
        password="adminpassword123"
    )
    user = await create_user(async_session, user_data)
    user.is_admin = True
    await async_session.commit()
    await async_session.refresh(user)
    return user


@pytest.fixture
async def test_products(async_session: AsyncSession) -> list[Product]:
    """Create test products."""
    products = [
        Product(
            name="Test Laptop",
            description="A high-performance test laptop",
            price=1299.99,
            stock=10,
            category="Electronics",
            sku="TEST-LAP-001",
            is_active=True
        ),
        Product(
            name="Test Phone",
            description="A modern test smartphone",
            price=699.99,
            stock=5,
            category="Electronics", 
            sku="TEST-PHN-001",
            is_active=True
        ),
        Product(
            name="Test Book",
            description="An educational test book",
            price=29.99,
            stock=20,
            category="Books",
            sku="TEST-BOK-001",
            is_active=True
        )
    ]
    
    for product in products:
        async_session.add(product)
    
    await async_session.commit()
    
    for product in products:
        await async_session.refresh(product)
    
    return products


@pytest.fixture
def auth_headers(test_user: User) -> dict[str, str]:
    """Generate authentication headers for test user."""
    from app.auth import create_access_token
    
    access_token = create_access_token(
        data={"sub": str(test_user.id), "email": test_user.email}
    )
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def admin_auth_headers(admin_user: User) -> dict[str, str]:
    """Generate authentication headers for admin user."""
    from app.auth import create_access_token
    
    access_token = create_access_token(
        data={"sub": str(admin_user.id), "email": admin_user.email}
    )
    return {"Authorization": f"Bearer {access_token}"}