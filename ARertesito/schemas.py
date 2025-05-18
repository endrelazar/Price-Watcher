# schemas.py

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
      

class ProductCreate(BaseModel):
    url: str
    target_price: float  
    name: Optional[str] = None  
    current_price: Optional[float] = None
    notify_interval_minutes: Optional[int] = 1440
    useremail: str

class ProductOut(BaseModel):
    id: int
    url: str
    name: str
    target_price: float
    current_price: Optional[float] = None
    last_checked: Optional[datetime] = None
    notify_interval_minutes: Optional[int] = 1440
    last_notified: Optional[datetime] = None
    useremail: str
    model_config = ConfigDict(from_attributes=True)
