import json
import time
from typing import AsyncGenerator, Optional

import httpx

from app.security import decrypt_api_key


def build_final_prompt(template: str, variables: dict) -> str:
    """Replace {{variable}} placeholders with actual values."""
    result = template
    for key, value in variables.items():
        result = result.replace("{{" + key + "}}", str(value))
    return result


async def stream_chat(
    api_base: str,
    api_key_encrypted: str,
    model: str,
    user_prompt: str,
    system_prompt: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
) -> AsyncGenerator[dict, None]:
    """Call OpenAI-compatible streaming chat API and yield event dicts."""
    api_key = decrypt_api_key(api_key_encrypted)
    url = f"{api_base.rstrip('/')}/chat/completions"

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})

    body = {
        "model": model,
        "messages": messages,
        "stream": True,
    }
    if temperature is not None:
        body["temperature"] = temperature
    if max_tokens is not None:
        body["max_tokens"] = max_tokens

    start_time = time.monotonic()

    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream("POST", url, json=body, headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }) as response:
            if response.status_code != 200:
                error_body = await response.aread()
                yield {"type": "error", "message": f"API error {response.status_code}: {error_body.decode()}"}
                return

            async for line in response.aiter_lines():
                if not line.startswith("data: "):
                    continue
                data_str = line[6:].strip()
                if data_str == "[DONE]":
                    break
                try:
                    chunk = json.loads(data_str)
                except json.JSONDecodeError:
                    continue

                if "choices" not in chunk or not chunk["choices"]:
                    continue

                delta = chunk["choices"][0].get("delta", {})
                content = delta.get("content", "")
                if content:
                    yield {"type": "token", "data": content}

                finish_reason = chunk["choices"][0].get("finish_reason")
                if finish_reason:
                    latency_ms = int((time.monotonic() - start_time) * 1000)
                    usage = chunk.get("usage", {})
                    yield {
                        "type": "done",
                        "usage": {
                            "prompt_tokens": usage.get("prompt_tokens", 0),
                            "completion_tokens": usage.get("completion_tokens", 0),
                        },
                        "latency_ms": latency_ms,
                    }
