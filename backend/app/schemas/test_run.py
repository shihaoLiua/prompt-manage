from pydantic import BaseModel
from typing import Any, Optional
import uuid
from datetime import datetime


class TestRunRequest(BaseModel):
    api_config_id: uuid.UUID
    model: str
    variables: dict[str, Any] = {}
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None


class TestRunResponse(BaseModel):
    id: uuid.UUID
    prompt_id: uuid.UUID
    model: str
    variables_snapshot: dict[str, Any]
    final_prompt: Optional[str] = None
    response_text: Optional[str] = None
    tokens_prompt: Optional[int] = None
    tokens_completion: Optional[int] = None
    latency_ms: Optional[int] = None
    status: str
    error_message: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
