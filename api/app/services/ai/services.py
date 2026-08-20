import httpx

from ...config import settings
from . import prompts
from .exceptions import AiDisabledError, AiEmptyMessageError, AiRequestError, AiUnavailableError


async def check_availability() -> bool:
  if not settings.ai_enabled:
    return False

  url = f"{settings.ai_base_url.rstrip('/')}/api/tags"
  try:
    async with httpx.AsyncClient(timeout=5.0) as client:
      response = await client.get(url)
      response.raise_for_status()
      return True
  except httpx.HTTPError:
    return False


async def chat(message: str) -> tuple[str, str]:
  if not settings.ai_enabled:
    raise AiDisabledError()

  text = message.strip()
  if not text:
    raise AiEmptyMessageError()

  url = f"{settings.ai_base_url.rstrip('/')}/api/chat"
  payload = {
    "model": settings.ai_model,
    "messages": [
      {"role": "system", "content": prompts.SYSTEM_PROMPT},
      {"role": "user", "content": text},
    ],
    "stream": False,
  }

  try:
    async with httpx.AsyncClient(timeout=settings.ai_timeout_seconds) as client:
      response = await client.post(url, json=payload)
      if response.status_code == 404:
        raise AiUnavailableError(
          f"Model '{settings.ai_model}' is not available. Run: make ollama-pull"
        )
      response.raise_for_status()
      data = response.json()
  except AiUnavailableError:
    raise
  except httpx.HTTPError as exc:
    raise AiRequestError(str(exc)) from exc

  reply = data.get("message", {}).get("content", "").strip()
  if not reply:
    raise AiRequestError("Empty response from AI")

  return reply, settings.ai_model