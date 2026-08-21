import httpx

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from ...config import settings
from ...models.ai_message import AiMessage
from ...schemas.ai import AiEventDraft
from .exceptions import AiDisabledError, AiEmptyMessageError, AiRequestError, AiUnavailableError
from . import helpers
from . import prompts


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


async def list_user_messages(
  db: AsyncSession,
  user_id: int,
  skip: int = 0,
  limit: int | None = 50,
) -> tuple[list[AiMessage], int]:
  total = await db.scalar(
    select(func.count()).select_from(AiMessage).where(AiMessage.user_id == user_id)
  ) or 0

  result = await db.execute(
    select(AiMessage)
    .where(AiMessage.user_id == user_id)
    .order_by(AiMessage.created_at.asc())
    .offset(skip)
    .limit(limit)
  )
  return list(result.scalars().all()), total


async def get_recent_history(db: AsyncSession, user_id: int, limit: int = 30) -> list[AiMessage]:
  result = await db.execute(
    select(AiMessage)
    .where(AiMessage.user_id == user_id)
    .order_by(AiMessage.created_at.desc())
    .limit(limit)
  )
  rows = list(result.scalars().all())
  rows.reverse()
  return rows


async def save_message(
  db: AsyncSession,
  user_id: int,
  role: str,
  content: str,
) -> AiMessage:
  message = AiMessage(user_id=user_id, role=role, content=content.strip())
  db.add(message)
  await db.commit()
  await db.refresh(message)
  return message


async def clear_user_messages(db: AsyncSession, user_id: int) -> None:
  await db.execute(delete(AiMessage).where(AiMessage.user_id == user_id))
  await db.commit()


async def call_ollama(messages: list[dict]) -> str:
  url = f"{settings.ai_base_url.rstrip('/')}/api/chat"
  payload = {
    "model": settings.ai_model,
    "messages": messages,
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
  return reply


async def chat_with_memory(
  db: AsyncSession,
  user_id: int,
  message: str,
  user_timezone: str = "UTC",
) -> tuple[str, str, AiMessage, AiMessage, AiEventDraft | None, bool]:
  if not settings.ai_enabled:
    raise AiDisabledError()

  text = message.strip()
  if not text:
    raise AiEmptyMessageError()

  history_rows = await get_recent_history(db, user_id)
  history = helpers.history_from_db_rows(history_rows)

  user_message = await save_message(db, user_id, "user", text)

  draft: AiEventDraft | None = None
  ready_to_create = False

  if helpers.is_event_creation_context(text, history):
    from .event_actions import extract_event_draft

    reply_language = helpers.detect_reply_language(text, history)
    draft_context = helpers.build_event_draft_context(history, text)
    reply_text, draft, ready_to_create = await extract_event_draft(
      draft_context,
      user_timezone,
      reply_language,
    )
  else:
    ollama_messages = helpers.build_ollama_messages(history, text, user_timezone)
    reply_text = await call_ollama(ollama_messages)

  assistant_message = await save_message(db, user_id, "assistant", reply_text)
  return reply_text, settings.ai_model, user_message, assistant_message, draft, ready_to_create