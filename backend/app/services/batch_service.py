import asyncio
import time
import uuid
from typing import AsyncGenerator

import httpx

from app.database import async_session_factory
from app.models import TestRun, TestBatch, TestBatchStatus, TestRunStatus, Prompt, ApiConfig
from app.security import decrypt_api_key
from app.services.llm_service import build_final_prompt


async def run_batch_test(
    batch_id: uuid.UUID,
    prompt_id: uuid.UUID,
    user_id: uuid.UUID,
) -> AsyncGenerator[dict, None]:
    """Execute all configs in a batch concurrently and yield SSE progress events."""
    async with async_session_factory() as db:
        from sqlalchemy import select

        batch_result = await db.execute(select(TestBatch).where(TestBatch.id == batch_id))
        batch = batch_result.scalar_one_or_none()
        if not batch:
            yield {"type": "error", "message": "Batch not found"}
            return

        prompt_result = await db.execute(select(Prompt).where(Prompt.id == prompt_id))
        prompt_obj = prompt_result.scalar_one_or_none()
        if not prompt_obj:
            yield {"type": "error", "message": "Prompt not found"}
            return

        config_list = batch.configs
        batch.status = TestBatchStatus.RUNNING
        batch.total_count = len(config_list)
        batch.completed_count = 0
        await db.commit()

        test_runs = []
        for cfg in config_list:
            cid = cfg["api_config_id"]
            if isinstance(cid, str):
                cid = uuid.UUID(cid)
            run = TestRun(
                id=uuid.uuid4(),
                prompt_id=prompt_id,
                user_id=user_id,
                api_config_id=cid,
                model=cfg["model"],
                batch_id=batch.id,
                status=TestRunStatus.RUNNING,
            )
            db.add(run)
            test_runs.append(run)
        await db.commit()

        async def execute_one(cfg, run):
            try:
                config_result = await db.execute(
                    select(ApiConfig).where(ApiConfig.id == run.api_config_id)
                )
                api_config = config_result.scalar_one_or_none()
                if not api_config:
                    raise ValueError(f"API config not found: {run.api_config_id}")

                api_key = decrypt_api_key(api_config.api_key_encrypted)
                final_prompt = build_final_prompt(prompt_obj.content, cfg.get("variables", {}))
                run.final_prompt = final_prompt

                url = f"{api_config.api_base.rstrip('/')}/chat/completions"
                messages = [{"role": "user", "content": final_prompt}]
                body = {"model": cfg["model"], "messages": messages, "stream": False}
                if cfg.get("temperature"):
                    body["temperature"] = cfg["temperature"]
                if cfg.get("max_tokens"):
                    body["max_tokens"] = cfg["max_tokens"]

                start = time.monotonic()
                async with httpx.AsyncClient(timeout=120.0) as client:
                    resp = await client.post(url, json=body, headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    })
                    latency = int((time.monotonic() - start) * 1000)

                if resp.status_code != 200:
                    raise ValueError(f"API error {resp.status_code}: {resp.text}")

                result = resp.json()
                run.response_text = result["choices"][0]["message"]["content"]
                run.tokens_prompt = result.get("usage", {}).get("prompt_tokens", 0)
                run.tokens_completion = result.get("usage", {}).get("completion_tokens", 0)
                run.latency_ms = latency
                run.status = TestRunStatus.SUCCESS
                return {"label": cfg.get("label", ""), "model": cfg["model"], "status": "success"}

            except Exception as e:
                run.status = TestRunStatus.ERROR
                run.error_message = str(e)
                return {"label": cfg.get("label", ""), "model": cfg["model"], "status": "error", "error": str(e)}

        sem = asyncio.Semaphore(5)

        async def limited(cfg, run):
            async with sem:
                return await execute_one(cfg, run)

        tasks = [limited(cfg, run) for cfg, run in zip(config_list, test_runs)]

        for coro in asyncio.as_completed(tasks):
            result = await coro
            batch.completed_count += 1
            yield {"type": "progress", "completed": batch.completed_count, "total": batch.total_count, "result": result}
            await db.commit()

        has_error = any(r.status == TestRunStatus.ERROR for r in test_runs)
        has_success = any(r.status == TestRunStatus.SUCCESS for r in test_runs)
        if has_error and has_success:
            batch.status = TestBatchStatus.PARTIAL
        elif has_error:
            batch.status = TestBatchStatus.FAILED
        else:
            batch.status = TestBatchStatus.COMPLETED
        await db.commit()

        yield {"type": "complete", "batch_id": str(batch.id), "status": batch.status.value}
