from fastapi import APIRouter, Depends, HTTPException
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from ..redis_client import get_redis

from ..config import settings
from ..database import get_db
from ..dependencies import get_current_user
from ..models.user import User
from ..schemas.ai import (
  AiChatRequest,
  AiChatResponse,
  AiEventCreateResponse,
  AiEventDraft,
  AiEventDraftResponse,
  AiHealthResponse,
  AiMessageOut,
  AiMessagesListOut,
)
from ..services import ai as ai_service
from ..services import events as events_service
from ..services.ai import helpers as ai_helpers

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/health", response_model=AiHealthResponse, summary="Check AI service status")
async def ai_health(current_user: User = Depends(get_current_user)):
  available = await ai_service.check_availability() if settings.ai_enabled else False
  return AiHealthResponse(
    enabled=settings.ai_enabled,
    available=available,
    model=settings.ai_model,
  )


@router.get("/messages", response_model=AiMessagesListOut)
async def list_ai_messages(
  skip: int = 0,
  limit: int | None = 50,
  db: AsyncSession = Depends(get_db),
  current_user: User = Depends(get_current_user),
):
  rows, total = await ai_service.list_user_messages(db, current_user.id, skip, limit)
  return AiMessagesListOut(
    items=[AiMessageOut.model_validate(row) for row in rows],
    total=total,
  )


@router.delete("/messages", status_code=204)
async def clear_ai_messages(
  db: AsyncSession = Depends(get_db),
  current_user: User = Depends(get_current_user),
):
  await ai_service.clear_user_messages(db, current_user.id)


@router.post("/chat", response_model=AiChatResponse)
async def ai_chat(
  body: AiChatRequest,
  db: AsyncSession = Depends(get_db),
  current_user: User = Depends(get_current_user),
):
  try:
    reply, model, user_msg, assistant_msg, draft, ready = await ai_service.chat_with_memory(
      db,
      current_user.id,
      body.message,
      current_user.timezone,
    )
    return AiChatResponse(
      reply=reply,
      model=model,
      user_message_id=user_msg.id,
      assistant_message_id=assistant_msg.id,
      draft=draft,
      ready_to_create=ready,
    )
  except ai_service.AiDisabledError:
    raise HTTPException(503, detail={"message": "AI is disabled", "field": "ai"})
  except ai_service.AiEmptyMessageError:
    raise HTTPException(400, detail={"message": "Message cannot be empty", "field": "message"})
  except ai_service.AiUnavailableError as exc:
    raise HTTPException(503, detail={"message": str(exc), "field": "ai"})
  except ai_service.AiRequestError as exc:
    raise HTTPException(502, detail={"message": f"AI request failed: {exc}", "field": "ai"})


@router.post("/events/draft", response_model=AiEventDraftResponse)
async def ai_event_draft(
  body: AiChatRequest,
  db: AsyncSession = Depends(get_db),
  current_user: User = Depends(get_current_user),
):
  reply_language = ai_helpers.detect_reply_language(body.message)
  reply, draft, ready = await ai_service.extract_event_draft(
    body.message,
    current_user.timezone,
    reply_language,
  )
  return AiEventDraftResponse(reply=reply, draft=draft, ready_to_create=ready)


@router.post("/events/create", response_model=AiEventCreateResponse)
async def ai_create_event(
  draft: AiEventDraft,
  db: AsyncSession = Depends(get_db),
  current_user: User = Depends(get_current_user),
  redis: Redis = Depends(get_redis),
):
  event = await ai_service.create_event_from_draft(db, current_user.id, draft)
  await events_service.invalidate_event_lists(redis, current_user.id)
  event_out = await events_service.build_event_out(db, event)
  history_rows = await ai_service.get_recent_history(db, current_user.id, limit=10)
  reply_language = ai_helpers.detect_reply_language(
    "",
    ai_helpers.history_from_db_rows(history_rows),
  )
  success_reply = (
    "Событие успешно создано."
    if reply_language == "Russian"
    else "Event created successfully."
  )
  return AiEventCreateResponse(
    reply=success_reply,
    event=event_out,
  )