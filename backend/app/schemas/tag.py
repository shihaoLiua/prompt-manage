from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime


class TagCreate(BaseModel):
    name: str
    color: Optional[str] = None


class TagUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None


class TagResponse(BaseModel):
    id: uuid.UUID
    name: str
    color: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
