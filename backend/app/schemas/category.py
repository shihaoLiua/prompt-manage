from pydantic import BaseModel
from typing import Optional, List
import uuid
from datetime import datetime


class CategoryCreate(BaseModel):
    name: str
    parent_id: Optional[uuid.UUID] = None
    sort_order: int = 0


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[uuid.UUID] = None
    sort_order: Optional[int] = None


class CategoryResponse(BaseModel):
    id: uuid.UUID
    name: str
    parent_id: Optional[uuid.UUID] = None
    sort_order: int
    created_at: datetime
    children: List["CategoryResponse"] = []

    model_config = {"from_attributes": True}
