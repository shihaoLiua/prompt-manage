from pydantic import BaseModel
from typing import Any, Optional
import uuid
from datetime import datetime


class PromptCreate(BaseModel):
    title: str
    content: str
    description: Optional[str] = None
    variables: list[dict[str, Any]] = []
    category_id: Optional[uuid.UUID] = None
    tag_ids: list[uuid.UUID] = []


class PromptUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    description: Optional[str] = None
    variables: Optional[list[dict[str, Any]]] = None
    category_id: Optional[uuid.UUID] = None
    tag_ids: Optional[list[uuid.UUID]] = None
    create_version: bool = True


class PromptResponse(BaseModel):
    id: uuid.UUID
    title: str
    content: str
    description: Optional[str] = None
    variables: list[dict[str, Any]] = []
    category_id: Optional[uuid.UUID] = None
    is_favorite: bool
    rating: Optional[int] = None
    current_version: int
    tags: list["TagResponse"] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PromptListItem(BaseModel):
    id: uuid.UUID
    title: str
    description: Optional[str] = None
    category_id: Optional[uuid.UUID] = None
    is_favorite: bool
    rating: Optional[int] = None
    current_version: int
    tags: list["TagResponse"] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PromptVersionResponse(BaseModel):
    id: uuid.UUID
    version: int
    content: str
    variables: list[dict[str, Any]]
    changelog: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ToggleFavoriteResponse(BaseModel):
    is_favorite: bool


class SetRatingRequest(BaseModel):
    rating: int


class PromptVersionCreate(BaseModel):
    content: str
    variables: list[dict[str, Any]] = []
    changelog: Optional[str] = None


# 延迟解析 forward ref
from app.schemas.tag import TagResponse
PromptResponse.model_rebuild()
PromptListItem.model_rebuild()
