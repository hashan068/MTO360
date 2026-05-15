"""
Database configuration and session management
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from typing import AsyncGenerator, Generator

from app.config.settings import settings
from app.models.base import Base


# Create async engine
engine = create_async_engine(
    settings.get_database_url(),
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


_sync_url = settings.get_database_url().replace("+asyncpg", "")
_sync_engine = create_engine(_sync_url, pool_pre_ping=True, pool_size=5)
SyncSessionLocal = sessionmaker(bind=_sync_engine, autocommit=False, autoflush=False)


def get_sync_db() -> Generator[Session, None, None]:
    """Sync DB session for quality module (uses legacy .query() ORM style)."""
    db = SyncSessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database (create tables)"""
    async with engine.begin() as conn:
        # Import all models here to ensure they are registered
        from app.models import (
            User,
            Supplier,
            Category,
            Component,
            PurchaseRequisition,
            PurchaseOrder,
            ReplenishTransaction,
            ConsumptionTransaction,
            Customer,
            Product,
            RFQ,
            RFQItem,
            Quotation,
            QuotationItem,
            SalesOrder,
            SalesOrderItem,
            ManufacturingOrder,
            MaterialRequisition,
            MaterialRequisitionItem,
            BillOfMaterial,
            BOMItem,
            WorkCenter,
            OperationRoute,
            RouteOperation,
            ManufacturingOrderOperation,
            WorkCenterSchedule,
            Notification,
        )
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close database connections"""
    await engine.dispose()

