"""
Pytest configuration and fixtures for integration tests
"""
import asyncio
import pytest
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.models.base import Base
from app.dependencies import get_database_session


# Test database URL (using SQLite for simplicity)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True,
)

# Create test session factory
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()
    
    # Drop tables after test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with database session override."""
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_database_session] = override_get_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
async def auth_headers(client: AsyncClient, db_session: AsyncSession) -> dict:
    """Create an authenticated user and return auth headers."""
    from app.models.user import User
    from passlib.context import CryptContext
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    # Create test user
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=pwd_context.hash("testpass123"),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # Login to get token
    response = await client.post(
        "/api/auth/login",
        data={"username": "testuser", "password": "testpass123"}
    )
    
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def test_customer(db_session: AsyncSession):
    """Create a test customer."""
    from app.models.customer import Customer
    
    customer = Customer(
        name="Test Customer Inc.",
        email="customer@test.com",
        phone="123-456-7890",
        address="123 Test St",
        is_active=True,
    )
    db_session.add(customer)
    await db_session.commit()
    await db_session.refresh(customer)
    
    return customer


@pytest.fixture
async def test_products(db_session: AsyncSession):
    """Create test products."""
    from app.models.product import Product
    
    products = [
        Product(
            name="Product A",
            description="Test Product A",
            unit_price=100.00,
            is_active=True,
        ),
        Product(
            name="Product B",
            description="Test Product B",
            unit_price=200.00,
            is_active=True,
        ),
    ]
    
    for product in products:
        db_session.add(product)
    
    await db_session.commit()
    
    for product in products:
        await db_session.refresh(product)
    
    return products
