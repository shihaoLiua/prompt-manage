import json
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from app.database import get_db
from app.models import Prompt, ApiConfig, TestRun, TestRunStatus, User
from app.schemas.test_run import TestRunRequest, TestRunResponse
from app.dependencies import get_current_user
from app.services.llm_service import build_final_prompt, stream_chat

router = APIRouter(tags=["test-runs"])


@router.post("/api/prompts/{prompt_id}/test")
async def test_prompt_stream(
    prompt_id: uuid.UUID,
    req: TestRunRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Stream a prompt test via SSE."""
    prompt_result = await db.execute(
        select(Prompt).where(Prompt.id == prompt_id, Prompt.user_id == current_user.id)
    )
    prompt = prompt_result.scalar_one_or_none()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    config_result = await db.execute(
        select(ApiConfig).where(
            ApiConfig.id == req.api_config_id,
            ((ApiConfig.user_id == current_user.id) | (ApiConfig.user_id.is_(None))),
            ApiConfig.is_active == True,
        )
    )
    api_config = config_result.scalar_one_or_none()
    if not api_config:
        raise HTTPException(status_code=404, detail="API config not found or inactive")

    final_prompt = build_final_prompt(prompt.content, req.variables)

    test_run = TestRun(
        id=uuid.uuid4(),
        prompt_id=prompt.id,
        user_id=current_user.id,
        api_config_id=api_config.id,
        model=req.model,
        variables_snapshot=req.variables,
        final_prompt=final_prompt,
        status=TestRunStatus.RUNNING,
    )
    db.add(test_run)
    await db.flush()

    async def event_generator():
        full_response = ""
        prompt_tokens = 0
        completion_tokens = 0
        latency_ms = 0
        error_msg = None

        try:
            async for event in stream_chat(
                api_base=api_config.api_base,
                api_key_encrypted=api_config.api_key_encrypted,
                model=req.model,
                user_prompt=final_prompt,
                temperature=req.temperature,
                max_tokens=req.max_tokens,
            ):
                if event["type"] == "token":
                    full_response += event["data"]
                    yield {"event": "token", "data": json.dumps(event)}
                elif event["type"] == "done":
                    prompt_tokens = event["usage"]["prompt_tokens"]
                    completion_tokens = event["usage"]["completion_tokens"]
                    latency_ms = event["latency_ms"]
                    yield {"event": "done", "data": json.dumps(event)}
                elif event["type"] == "error":
                    error_msg = event["message"]
                    yield {"event": "error", "data": json.dumps(event)}
        except Exception as e:
            error_msg = str(e)
            yield {"event": "error", "data": json.dumps({"type": "error", "message": str(e)})}
        finally:
            test_run.response_text = full_response
            test_run.tokens_prompt = prompt_tokens
            test_run.tokens_completion = completion_tokens
            test_run.latency_ms = latency_ms
            test_run.status = TestRunStatus.ERROR if error_msg else TestRunStatus.SUCCESS
            test_run.error_message = error_msg
            await db.commit()

    return EventSourceResponse(event_generator())


@router.get("/api/prompts/{prompt_id}/test-runs", response_model=list[TestRunResponse])
async def list_test_runs(
    prompt_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TestRun).where(
            TestRun.prompt_id == prompt_id,
            TestRun.user_id == current_user.id,
        ).order_by(TestRun.created_at.desc()).limit(50)
    )
    return result.scalars().all()


@router.get("/api/test-runs/{run_id}", response_model=TestRunResponse)
async def get_test_run(
    run_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TestRun).where(TestRun.id == run_id, TestRun.user_id == current_user.id)
    )
    test_run = result.scalar_one_or_none()
    if not test_run:
        raise HTTPException(status_code=404, detail="Test run not found")
    return test_run


@router.delete("/api/test-runs/{run_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_test_run(
    run_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TestRun).where(TestRun.id == run_id, TestRun.user_id == current_user.id)
    )
    test_run = result.scalar_one_or_none()
    if not test_run:
        raise HTTPException(status_code=404, detail="Test run not found")
    await db.delete(test_run)
    return None
