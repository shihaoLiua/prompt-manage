from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime


class UserResponse(BaseModel):
    id: uuid.UUID
    username: str
    email: str
    is_admin: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UpdateUserRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None


class ApiConfigCreate(BaseModel):
    name: str
    api_base: str
    api_key: str
    default_model: str


class ApiConfigUpdate(BaseModel):
    name: Optional[str] = None
    api_base: Optional[str] = None
    api_key: Optional[str] = None
    default_model: Optional[str] = None


class ApiConfigResponse(BaseModel):
    id: uuid.UUID
    name: str
    api_base: str
    default_model: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
