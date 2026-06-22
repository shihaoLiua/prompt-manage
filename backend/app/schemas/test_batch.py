from pydantic import BaseModel
from typing import Any, Optional
import uuid
from datetime import datetime


class BatchConfig(BaseModel):
    api_config_id: uuid.UUID
    model: str
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    label: str = ""


class BatchTestRequest(BaseModel):
    name: str
    configs: list[BatchConfig]
    variables: dict[str, Any] = {}


class BatchTestResponse(BaseModel):
    id: uuid.UUID
    prompt_id: uuid.UUID
    name: str
    status: str
    total_count: int
    completed_count: int
    created_at: datetime

    model_config = {"from_attributes": True}
