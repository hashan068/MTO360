"""
Unit tests for SchedulingService

This demonstrates testing patterns for async services with database operations.
Expand these examples to cover all service methods.
"""
import pytest
from datetime import datetime, date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.models.manufacturing import (
    ManufacturingOrder,
    ManufacturingOrderOperation,
    OperationRoute,
    RouteOperation,
    WorkCenter,
    OperationStatusEnum,
    ManufacturingOrderStatusEnum,
)
from app.modules.manufacturing.application.services.scheduling_service import (
    SchedulingService,
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

    # Create all tables
    async with engine.begin() as conn:
        from app.models.base import Base
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session

    # Cleanup
    await engine.dispose()


@pytest.fixture
async def work_center(db_session: AsyncSession):
    """Create a test work center"""
    wc = WorkCenter(
        name="Test Assembly Station",
        code="TEST-AS-01",
        capacity_hours_per_day=8.0,
        is_active=True,
    )
    db_session.add(wc)
    await db_session.commit()
    await db_session.refresh(wc)
    return wc


@pytest.fixture
async def operation_route(db_session: AsyncSession, work_center: WorkCenter):
    """Create a test operation route with operations"""
    route = OperationRoute(
        name="Test Route",
        product_id=1,
        is_active=True,
    )
    db_session.add(route)
    await db_session.flush()

    # Add route operations
    op1 = RouteOperation(
        route_id=route.id,
        sequence=1,
        name="Assembly",
        work_center_id=work_center.id,
        standard_time_minutes=30,
        setup_time_minutes=15,
    )
    op2 = RouteOperation(
        route_id=route.id,
        sequence=2,
        name="Testing",
        work_center_id=work_center.id,
        standard_time_minutes=20,
        setup_time_minutes=10,
    )
    db_session.add_all([op1, op2])
    await db_session.commit()
    await db_session.refresh(route)

    return route


@pytest.fixture
async def manufacturing_order(db_session: AsyncSession):
    """Create a test manufacturing order"""
    mo = ManufacturingOrder(
        product_id=1,
        quantity=5,
        status=ManufacturingOrderStatusEnum.PENDING,
    )
    db_session.add(mo)
    await db_session.commit()
    await db_session.refresh(mo)
    return mo


class TestSchedulingService:
    """Test cases for SchedulingService"""

    @pytest.mark.asyncio
    async def test_generate_operations_for_mo(
        self,
        db_session: AsyncSession,
        manufacturing_order: ManufacturingOrder,
        operation_route: OperationRoute,
    ):
        """Test generating operations from route template"""
        service = SchedulingService(db_session)

        # Generate operations
        operations = await service.generate_operations_for_mo(manufacturing_order.id)

        # Assertions
        assert len(operations) == 2
        assert operations[0].sequence == 1
        assert operations[0].name == "Assembly"
        assert operations[0].status == OperationStatusEnum.PENDING
        assert operations[0].scheduled_duration_minutes == 45  # 30 + 15

        assert operations[1].sequence == 2
        assert operations[1].name == "Testing"
        assert operations[1].scheduled_duration_minutes == 30  # 20 + 10

    @pytest.mark.asyncio
    async def test_generate_operations_no_route(
        self,
        db_session: AsyncSession,
        manufacturing_order: ManufacturingOrder,
    ):
        """Test error handling when no route exists"""
        service = SchedulingService(db_session)

        # Should raise ValueError
        with pytest.raises(ValueError, match="No active operation route found"):
            await service.generate_operations_for_mo(manufacturing_order.id)

    @pytest.mark.asyncio
    async def test_calculate_work_center_capacity(
        self,
        db_session: AsyncSession,
        work_center: WorkCenter,
    ):
        """Test capacity calculation"""
        service = SchedulingService(db_session)

        target_date = date.today()
        capacity = await service.calculate_work_center_capacity(
            work_center.id, target_date
        )

        # Assertions
        assert capacity["capacity_minutes"] == 480  # 8 hours * 60
        assert capacity["scheduled_minutes"] == 0  # No operations yet
        assert capacity["available_minutes"] == 480
        assert capacity["utilization_pct"] == 0.0

    @pytest.mark.asyncio
    async def test_find_available_slot(
        self,
        db_session: AsyncSession,
        work_center: WorkCenter,
    ):
        """Test finding available time slot"""
        service = SchedulingService(db_session)

        duration = 60  # 1 hour
        after_time = datetime.utcnow()

        slot = await service.find_available_slot(
            work_center.id, duration, after_time
        )

        # Assertions
        assert slot["start_datetime"] >= after_time
        assert slot["end_datetime"] > slot["start_datetime"]
        
        # Duration should match
        duration_delta = slot["end_datetime"] - slot["start_datetime"]
        assert duration_delta.total_seconds() / 60 == duration

    @pytest.mark.asyncio
    async def test_detect_scheduling_conflicts(
        self,
        db_session: AsyncSession,
        work_center: WorkCenter,
        manufacturing_order: ManufacturingOrder,
    ):
        """Test conflict detection"""
        service = SchedulingService(db_session)

        # Create an operation
        op = ManufacturingOrderOperation(
            manufacturing_order_id=manufacturing_order.id,
            sequence=1,
            name="Test Op",
            work_center_id=work_center.id,
            scheduled_duration_minutes=60,
            status=OperationStatusEnum.SCHEDULED,
            scheduled_start=datetime(2025, 1, 15, 8, 0, 0),
            scheduled_end=datetime(2025, 1, 15, 9, 0, 0),
        )
        db_session.add(op)
        await db_session.commit()

        # Test overlapping time range
        conflicts = await service.detect_scheduling_conflicts(
            work_center.id,
            datetime(2025, 1, 15, 8, 30, 0),  # Overlaps with existing
            datetime(2025, 1, 15, 9, 30, 0),
        )

        assert len(conflicts) == 1
        assert conflicts[0].id == op.id

        # Test non-overlapping time range
        no_conflicts = await service.detect_scheduling_conflicts(
            work_center.id,
            datetime(2025, 1, 15, 10, 0, 0),  # No overlap
            datetime(2025, 1, 15, 11, 0, 0),
        )

        assert len(no_conflicts) == 0


# Run with: pytest tests/modules/manufacturing/test_scheduling_service.py -v
