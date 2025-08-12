from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class Farm(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    location: str
    size_hectares: float
    soil_type: Optional[str] = None
    irrigation_type: Optional[str] = None
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Foreign keys
    farmer_id: int = Field(foreign_key="user.id")
    
    # Relationships
    listings: List["Listing"] = Relationship(back_populates="farm")
    
    class Config:
        arbitrary_types_allowed = True
