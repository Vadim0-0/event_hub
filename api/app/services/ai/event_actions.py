import json
import re

from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from ...schemas.ai import AiEventDraft
from ...schemas.event import EventCreate
from ...services import events as events_service
from . import services as ai_services
from . import helpers
from . import prompts
from .exceptions import AiRequestError


def parse_ai_json(text: str) -> dict:
  try:
    return json.loads(text)
  except json.JSONDecodeError:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
      raise ValueError("No JSON in AI response")
    return json.loads(match.group())


async def extract_event_draft(
  message: str,
  user_timezone: str,
  reply_language: str = "English",
) -> tuple[str, AiEventDraft | None, bool]:
  prompt = (
    f"{prompts.EVENT_EXTRACT_PROMPT}\n"
    f"{helpers.language_instruction(reply_language)}\n"
    f"User timezone: {user_timezone}\n"
    f"Conversation:\n{message}"
  )

  try:
    raw = await ai_services.call_ollama([
      {"role": "system", "content": prompt},
      {"role": "user", "content": message},
    ])
    data = parse_ai_json(raw)
  except (ValueError, AiRequestError):
    fallback = (
      "Не удалось разобрать данные события."
      if reply_language == "Russian"
      else "Could not parse event details."
    )
    return fallback, None, False

  draft = None
  if data.get("draft"):
    try:
      draft = AiEventDraft.model_validate(data["draft"])
    except ValidationError:
      draft = None

  ready = bool(data.get("ready_to_create")) and draft is not None
  return data.get("reply", ""), draft, ready


async def create_event_from_draft(
  db: AsyncSession,
  creator_id: int,
  draft: AiEventDraft,
):
  event_data = EventCreate(
    title=draft.title,
    description=draft.description,
    starts_at=draft.starts_at,
    location=draft.location,
    latitude=draft.latitude,
    longitude=draft.longitude,
    max_participants=draft.max_participants,
  )
  return await events_service.create_event(event_data, db, creator_id)