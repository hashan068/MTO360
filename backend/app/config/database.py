"""
Database configuration and session management
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from typing import AsyncGenerator

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


class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


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
            Notification,
        )
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close database connections"""
    await engine.dispose()

