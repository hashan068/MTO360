"""
Unit tests for ShopFloorService

Demonstrates testing operation lifecycle, status transitions, and validation logic.
"""
import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.models.manufacturing import (
    ManufacturingOrder,
    ManufacturingOrderOperation,
    WorkCenter,
    OperationStatusEnum,
    ManufacturingOrderStatusEnum,
)
from app.modules.manufacturing.application.services.shop_floor_service import (
    ShopFloorService,
)


# Test database setup
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def db_session():
    """Create an async test database session"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
        echo=False,
    )

    async with engine.begin() as conn:
        from app.models.base import Base
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session

    await engine.dispose()


@pytest.fixture
async def work_center(db_session: AsyncSession):
    """Create test work center"""
    wc = WorkCenter(
        name="Test Station",
        code="TEST-01",
        capacity_hours_per_day=8.0,
        is_active=True,
    )
    db_session.add(wc)
    await db_session.commit()
    await db_session.refresh(wc)
    return wc


@pytest.fixture
async def manufacturing_order(db_session: AsyncSession):
    """Create test manufacturing order"""
    mo = ManufacturingOrder(
        product_id=1,
        quantity=5,
        status=ManufacturingOrderStatusEnum.MR_APPROVED,
    )
    db_session.add(mo)
    await db_session.commit()
    await db_session.refresh(mo)
    return mo


@pytest.fixture
async def scheduled_operation(
    db_session: AsyncSession,
    manufacturing_order: ManufacturingOrder,
    work_center: WorkCenter,
):
    """Create a scheduled operation"""
    op = ManufacturingOrderOperation(
        manufacturing_order_id=manufacturing_order.id,
        sequence=1,
        name="Assembly",
        work_center_id=work_center.id,
        scheduled_duration_minutes=45,
        status=OperationStatusEnum.SCHEDULED,
        scheduled_start=datetime(2025, 1, 15, 8, 0, 0),
        scheduled_end=datetime(2025, 1, 15, 8, 45, 0),
    )
    db_session.add(op)
    await db_session.commit()
    await db_session.refresh(op)
    return op


class TestShopFloorService:
    """Test cases for ShopFloorService"""

    @pytest.mark.asyncio
    async def test_start_operation(
        self,
        db_session: AsyncSession,
        scheduled_operation: ManufacturingOrderOperation,
    ):
        """Test starting an operation"""
        service = ShopFloorService(db_session)

        operator_id = 100
        operation = await service.start_operation(
            scheduled_operation.id, operator_id
        )

        # Assertions
        assert operation.status == OperationStatusEnum.IN_PROGRESS
        assert operation.actual_start is not None
        assert operation.assigned_operator_id == operator_id

    @pytest.mark.asyncio
    async def test_start_operation_invalid_status(
        self,
        db_session: AsyncSession,
        scheduled_operation: ManufacturingOrderOperation,
    ):
        """Test that completed operations cannot be started"""
        scheduled_operation.status = OperationStatusEnum.COMPLETED
        await db_session.commit()

        service = ShopFloorService(db_session)

        with pytest.raises(ValueError, match="Cannot start operation with status"):
            await service.start_operation(scheduled_operation.id)

    @pytest.mark.asyncio
    async def test_complete_operation(
        self,
        db_session: AsyncSession,
        scheduled_operation: ManufacturingOrderOperation,
    ):
        """Test completing an operation"""
        service = ShopFloorService(db_session)

        # First start the operation
        await service.start_operation(scheduled_operation.id)

        # Then complete it
        operation = await service.complete_operation(scheduled_operation.id)

        # Assertions
        assert operation.status == OperationStatusEnum.COMPLETED
        assert operation.actual_start is not None
        assert operation.actual_end is not None
        assert operation.actual_duration_minutes is not None
        assert operation.actual_duration_minutes > 0

    @pytest.mark.asyncio
    async def test_complete_operation_not_started(
        self,
        db_session: AsyncSession,
        scheduled_operation: ManufacturingOrderOperation,
    ):
        """Test that non-started operations cannot be completed"""
        service = ShopFloorService(db_session)

        with pytest.raises(ValueError, match="Cannot complete operation"):
            await service.complete_operation(scheduled_operation.id)

    @pytest.mark.asyncio
    async def test_block_operation(
        self,
        db_session: AsyncSession,
        scheduled_operation: ManufacturingOrderOperation,
    ):
        """Test blocking an operation"""
        service = ShopFloorService(db_session)

        blocking_reason = "Equipment malfunction"
        operation = await service.block_operation(
            scheduled_operation.id, blocking_reason
        )

        # Assertions
        assert operation.status == OperationStatusEnum.BLOCKED
        assert operation.blocking_reason == blocking_reason

    @pytest.mark.asyncio
    async def test_unblock_operation(
        self,
        db_session: AsyncSession,
        scheduled_operation: ManufacturingOrderOperation,
    ):
        """Test unblocking an operation"""
        service = ShopFloorService(db_session)

        # First block it
        await service.block_operation(scheduled_operation.id, "Test block")

        # Then unblock
        operation = await service.unblock_operation(scheduled_operation.id)

        # Should return to SCHEDULED since it wasn't started
        assert operation.status == OperationStatusEnum.SCHEDULED
        assert operation.blocking_reason is None

    @pytest.mark.asyncio
    async def test_update_mo_status_all_completed(
        self,
        db_session: AsyncSession,
        manufacturing_order: ManufacturingOrder,
        work_center: WorkCenter,
    ):
        """Test MO status updates when all operations complete"""
        service = ShopFloorService(db_session)

        # Create and complete operations
        op1 = ManufacturingOrderOperation(
            manufacturing_order_id=manufacturing_order.id,
            sequence=1,
            name="Op 1",
            work_center_id=work_center.id,
            scheduled_duration_minutes=30,
            status=OperationStatusEnum.COMPLETED,
            actual_start=datetime.utcnow(),
            actual_end=datetime.utcnow(),
            actual_duration_minutes=30,
        )
        op2 = ManufacturingOrderOperation(
            manufacturing_order_id=manufacturing_order.id,
            sequence=2,
            name="Op 2",
            work_center_id=work_center.id,
            scheduled_duration_minutes=30,
            status=OperationStatusEnum.COMPLETED,
            actual_start=datetime.utcnow(),
            actual_end=datetime.utcnow(),
            actual_duration_minutes=30,
        )
        db_session.add_all([op1, op2])
        await db_session.commit()

        # Update MO status
        mo = await service.update_mo_status_from_operations(
            manufacturing_order.id
        )

        # All operations completed -> MO should be COMPLETED
        assert mo.status == ManufacturingOrderStatusEnum.COMPLETED
        assert mo.end_at is not None

    @pytest.mark.asyncio
    async def test_get_work_center_queue(
        self,
        db_session: AsyncSession,
        work_center: WorkCenter,
        manufacturing_order: ManufacturingOrder,
    ):
        """Test getting work center queue"""
        service = ShopFloorService(db_session)

        # Add operations to queue
        op1 = ManufacturingOrderOperation(
            manufacturing_order_id=manufacturing_order.id,
            sequence=1,
            name="Pending Op",
            work_center_id=work_center.id,
            scheduled_duration_minutes=30,
            status=OperationStatusEnum.PENDING,
        )
        op2 = ManufacturingOrderOperation(
            manufacturing_order_id=manufacturing_order.id,
            sequence=2,
            name="Scheduled Op",
            work_center_id=work_center.id,
            scheduled_duration_minutes=30,
            status=OperationStatusEnum.SCHEDULED,
            scheduled_start=datetime(2025, 1, 15, 10, 0, 0),
        )
        db_session.add_all([op1, op2])
        await db_session.commit()

        # Get queue
        queue = await service.get_work_center_queue(work_center.id)

        # Should return both operations
        assert len(queue) == 2
        assert queue[0]["operation_name"] in ["Pending Op", "Scheduled Op"]


# Run with: pytest tests/modules/manufacturing/test_shop_floor_service.py -v
