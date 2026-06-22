import json
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from app.database import get_db
from app.models import Prompt, TestBatch, TestBatchStatus, User
from app.schemas.test_batch import BatchTestRequest, BatchTestResponse
from app.dependencies import get_current_user
from app.services.batch_service import run_batch_test

router = APIRouter(tags=["batch-tests"])


@router.get("/api/batch-tests", response_model=list[BatchTestResponse])
async def list_batch_tests(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TestBatch).where(TestBatch.user_id == current_user.id)
        .order_by(TestBatch.created_at.desc()).limit(50)
    )
    return result.scalars().all()


@router.get("/api/batch-tests/{batch_id}", response_model=BatchTestResponse)
async def get_batch_test(
    batch_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TestBatch).where(TestBatch.id == batch_id, TestBatch.user_id == current_user.id)
    )
    batch = result.scalar_one_or_none()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    return batch


@router.get("/api/batch-tests/{batch_id}/stream")
async def stream_batch_progress(
    batch_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
):
    async def event_generator():
        async for event in run_batch_test(batch_id, uuid.UUID(int=0), current_user.id):
            yield {"event": event["type"], "data": json.dumps(event)}

    return EventSourceResponse(event_generator())


@router.post("/api/prompts/{prompt_id}/batch-test",
             response_model=BatchTestResponse, status_code=status.HTTP_201_CREATED)
async def create_batch_test(
    prompt_id: uuid.UUID,
    req: BatchTestRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    p_result = await db.execute(
        select(Prompt).where(Prompt.id == prompt_id, Prompt.user_id == current_user.id)
    )
    if not p_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Prompt not found")

    batch = TestBatch(
        id=uuid.uuid4(),
        user_id=current_user.id,
        prompt_id=prompt_id,
        name=req.name,
        configs=[c.model_dump(mode="json") for c in req.configs],
        status=TestBatchStatus.PENDING,
        total_count=len(req.configs),
        completed_count=0,
    )
    db.add(batch)
    await db.flush()
    await db.refresh(batch)
    return batch


@router.delete("/api/batch-tests/{batch_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_batch_test(
    batch_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TestBatch).where(TestBatch.id == batch_id, TestBatch.user_id == current_user.id)
    )
    batch = result.scalar_one_or_none()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    await db.delete(batch)
    return None
