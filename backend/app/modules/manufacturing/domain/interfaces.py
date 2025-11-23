"""
Manufacturing Domain Repository Interfaces

Protocol-based repository interfaces for manufacturing domain entities.
"""
from typing import Protocol, Optional, List
from datetime import datetime, timedelta, date

from app.models.manufacturing import (
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
)
from app.models.manufacturing import (
    ManufacturingOrderStatusEnum,
    MaterialRequisitionStatusEnum,
    MaterialRequisitionItemStatusEnum,
    OperationStatusEnum,
)


class ManufacturingOrderRepository(Protocol):
    """Repository interface for ManufacturingOrder"""
    
    async def get_by_id(self, order_id: int) -> Optional[ManufacturingOrder]: ...
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ManufacturingOrder]: ...
    
    async def create(self, *, sales_order_item_id: Optional[int] = None,
                     product_id: Optional[int] = None, quantity: int = 1,
                     bom_id: Optional[int] = None,
                     status: ManufacturingOrderStatusEnum = ManufacturingOrderStatusEnum.PENDING,
                     creator_id: Optional[int] = None) -> ManufacturingOrder: ...
    
    async def update(self, order_id: int, **kwargs) -> Optional[ManufacturingOrder]: ...
    
    async def delete(self, order_id: int) -> bool: ...


class MaterialRequisitionRepository(Protocol):
    """Repository interface for MaterialRequisition"""
    
    async def get_by_id(self, requisition_id: int) -> Optional[MaterialRequisition]: ...
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[MaterialRequisition]: ...
    
    async def create(self, *, manufacturing_order_id: int, bom_id: Optional[int] = None,
                     status: MaterialRequisitionStatusEnum = MaterialRequisitionStatusEnum.PENDING) -> MaterialRequisition: ...
    
    async def update(self, requisition_id: int, **kwargs) -> Optional[MaterialRequisition]: ...
    
    async def delete(self, requisition_id: int) -> bool: ...


class MaterialRequisitionItemRepository(Protocol):
    """Repository interface for MaterialRequisitionItem"""
    
    async def get_by_id(self, item_id: int) -> Optional[MaterialRequisitionItem]: ...
    
    async def get_by_requisition_id(self, requisition_id: int) -> List[MaterialRequisitionItem]: ...
    
    async def create(self, *, material_requisition_id: int, component_id: int,
                     quantity: int, status: MaterialRequisitionItemStatusEnum = MaterialRequisitionItemStatusEnum.PENDING) -> MaterialRequisitionItem: ...
    
    async def update(self, item_id: int, **kwargs) -> Optional[MaterialRequisitionItem]: ...
    
    async def delete(self, item_id: int) -> bool: ...


class BillOfMaterialRepository(Protocol):
    """Repository interface for BillOfMaterial"""
    
    async def get_by_id(self, bom_id: int) -> Optional[BillOfMaterial]: ...
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[BillOfMaterial]: ...
    
    async def get_by_product_id(self, product_id: int) -> Optional[BillOfMaterial]: ...
    
    async def create(self, *, name: str, product_id: Optional[int] = None) -> BillOfMaterial: ...
    
    async def update(self, bom_id: int, **kwargs) -> Optional[BillOfMaterial]: ...
    
    async def delete(self, bom_id: int) -> bool: ...


class BOMItemRepository(Protocol):
    """Repository interface for BOMItem"""
    
    async def get_by_id(self, item_id: int) -> Optional[BOMItem]: ...
    
    async def get_by_bom_id(self, bom_id: int) -> List[BOMItem]: ...
    
    async def create(self, *, bill_of_material_id: int, component_id: Optional[int] = None,
                     quantity: int) -> BOMItem: ...
    
    async def delete(self, item_id: int) -> bool: ...


# ========== Production Scheduling Repository Interfaces ==========

class WorkCenterRepository(Protocol):
    """Repository interface for WorkCenter"""
    
    async def get_by_id(self, work_center_id: int) -> Optional[WorkCenter]: ...
    
    async def get_all(self, skip: int = 0, limit: int = 100, active_only: bool = False) -> List[WorkCenter]: ...
    
    async def get_by_code(self, code: str) -> Optional[WorkCenter]: ...
    
    async def create(self, *, name: str, code: str, capacity_hours_per_day: float,
                     description: Optional[str] = None, is_active: bool = True,
                     location: Optional[str] = None, notes: Optional[str] = None) -> WorkCenter: ...
    
    async def update(self, work_center_id: int, **kwargs) -> Optional[WorkCenter]: ...
    
    async def delete(self, work_center_id: int) -> bool: ...


class OperationRouteRepository(Protocol):
    """Repository interface for OperationRoute"""
    
    async def get_by_id(self, route_id: int) -> Optional[OperationRoute]: ...
    
    async def get_all(self, skip: int = 0, limit: int = 100, active_only: bool = False) -> List[OperationRoute]: ...
    
    async def get_by_product_id(self, product_id: int) -> Optional[OperationRoute]: ...
    
    async def get_by_bom_id(self, bom_id: int) -> Optional[OperationRoute]: ...
    
    async def create(self, *, name: str, product_id: Optional[int] = None,
                     bom_id: Optional[int] = None, is_active: bool = True) -> OperationRoute: ...
    
    async def update(self, route_id: int, **kwargs) -> Optional[OperationRoute]: ...
    
    async def delete(self, route_id: int) -> bool: ...


class RouteOperationRepository(Protocol):
    """Repository interface for RouteOperation"""
    
    async def get_by_id(self, operation_id: int) -> Optional[RouteOperation]: ...
    
    async def get_by_route_id(self, route_id: int) -> List[RouteOperation]: ...
    
    async def create(self, *, route_id: int, sequence: int, name: str,
                     work_center_id: int, standard_time_minutes: int,
                     setup_time_minutes: int = 0, description: Optional[str] = None) -> RouteOperation: ...
    
    async def update(self, operation_id: int, **kwargs) -> Optional[RouteOperation]: ...
    
    async def delete(self, operation_id: int) -> bool: ...
    
    async def delete_by_route_id(self, route_id: int) -> bool: ...


class ManufacturingOrderOperationRepository(Protocol):
    """Repository interface for ManufacturingOrderOperation"""
    
    async def get_by_id(self, operation_id: int) -> Optional[ManufacturingOrderOperation]: ...
    
    async def get_by_mo_id(self, mo_id: int) -> List[ManufacturingOrderOperation]: ...
    
    async def get_by_work_center_id(self, work_center_id: int, 
                                     status: Optional[OperationStatusEnum] = None) -> List[ManufacturingOrderOperation]: ...
    
    async def get_by_operator_id(self, operator_id: int,
                                  status: Optional[OperationStatusEnum] = None) -> List[ManufacturingOrderOperation]: ...
    
    async def get_scheduled_between(self, work_center_id: int, start_date: datetime,
                                     end_date: datetime) -> List[ManufacturingOrderOperation]: ...
    
    async def create(self, *, manufacturing_order_id: int, sequence: int, name: str,
                     work_center_id: int, scheduled_duration_minutes: int,
                     route_operation_id: Optional[int] = None,
                     scheduled_start: Optional[datetime] = None,
                     scheduled_end: Optional[datetime] = None,
                     status: OperationStatusEnum = OperationStatusEnum.PENDING) -> ManufacturingOrderOperation: ...
    
    async def update(self, operation_id: int, **kwargs) -> Optional[ManufacturingOrderOperation]: ...
    
    async def delete(self, operation_id: int) -> bool: ...


class WorkCenterScheduleRepository(Protocol):
    """Repository interface for WorkCenterSchedule"""
    
    async def get_by_id(self, schedule_id: int) -> Optional[WorkCenterSchedule]: ...
    
    async def get_by_work_center_and_date(self, work_center_id: int, 
                                          schedule_date: date) -> Optional[WorkCenterSchedule]: ...
    
    async def get_by_work_center_date_range(self, work_center_id: int,
                                            start_date: date, end_date: date) -> List[WorkCenterSchedule]: ...
    
    async def create(self, *, work_center_id: int, date: date,
                     available_capacity_minutes: int,
                     scheduled_capacity_minutes: int = 0) -> WorkCenterSchedule: ...
    
    async def update(self, schedule_id: int, **kwargs) -> Optional[WorkCenterSchedule]: ...
    
    async def delete(self, schedule_id: int) -> bool: ...
