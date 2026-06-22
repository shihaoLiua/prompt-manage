import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, Integer, ForeignKey, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import enum

from app.database import Base


class TestRunStatus(str, enum.Enum):
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"


class TestRun(Base):
    __tablename__ = "test_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prompt_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("prompts.id"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    api_config_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("api_configs.id"), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    variables_snapshot: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    final_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    response_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    tokens_prompt: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tokens_completion: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[TestRunStatus] = mapped_column(SAEnum(TestRunStatus), nullable=False, default=TestRunStatus.RUNNING)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    batch_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("test_batches.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    prompt = relationship("Prompt", back_populates="test_runs")
    user = relationship("User", back_populates="test_runs")
    api_config = relationship("ApiConfig", back_populates="test_runs")
    batch = relationship("TestBatch", back_populates="test_runs")
