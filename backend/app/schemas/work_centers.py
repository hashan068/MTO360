from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class WorkCenterCreate(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    capacity_hours_per_day: float
    is_active: bool = True
    location: Optional[str] = None
    notes: Optional[str] = None


class WorkCenterUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    capacity_hours_per_day: Optional[float] = None
    is_active: Optional[bool] = None
    location: Optional[str] = None


class TestResponse(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str] = None
    capacity_hours_per_day: float
    is_active: bool
    location: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
