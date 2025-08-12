from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FarmCreate(BaseModel):
    name: str
    description: Optional[str] = None
    location: str
    size_hectares: float
    soil_type: Optional[str] = None
    irrigation_type: Optional[str] = None

class FarmResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    location: str
    size_hectares: float
    soil_type: Optional[str] = None
    irrigation_type: Optional[str] = None
    is_active: bool
    farmer_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class FarmUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    size_hectares: Optional[float] = None
    soil_type: Optional[str] = None
    irrigation_type: Optional[str] = None
    is_active: Optional[bool] = None
