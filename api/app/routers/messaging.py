from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from ..cache import cache_get, cache_set
from ..redis_client import get_redis
from ..config import settings
from ..database import get_db
from ..dependencies import get_current_user
from ..models.user import User
from ..schemas.messaging import (
  ConversationOut, ConversationsListOut, UnreadCountOut, MessageCreate, MessageOut, ConversationCreate
)
from ..services import messaging as messaging_service
from ..notifications import dispatch

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("/", response_model=ConversationsListOut)
async def list_conversations(
  skip: int = 0,
  limit: int = 20,
  search: str | None = None,
  db: AsyncSession = Depends(get_db),
  current_user: User = Depends(get_current_user),
  redis: Redis = Depends(get_redis),
):
  cache_key = (
    f"conversations:list:user={current_user.id}:"
    f"skip={skip}:limit={limit}:search={search or ''}"
  )

  cached = await cache_get(redis, cache_key)
  if cached is not None:
    return ConversationsListOut.model_validate(cached)

  conversations, total = await messaging_service.list_user_conversations(
    db,
    current_user.id,
    skip,
    limit,
    search=search,
  )
  items = [
    await messaging_service.build_conversation_out(db, c, current_user.id)
    for c in conversations
  ]

  data = ConversationsListOut(items=items, total=total).model_dump(mode="json")
  await cache_set(redis, cache_key, data, settings.cache_ttl_seconds)
  return ConversationsListOut.model_validate(data)


@router.post("/", response_model=ConversationOut, status_code=201)
async def start_conversation(
  data: ConversationCreate,
  db: AsyncSession = Depends(get_db),
  current_user: User = Depends(get_current_user),
  redis: Redis = Depends(get_redis),
):
  try:
    conversation = await messaging_service.get_or_create_conversation(
      db, current_user.id, data.recipient_id
    )
    await messaging_service.invalidate_for_both_participants(
      redis,
      conversation.user1_id,
      conversation.user2_id,
    )
    return await messaging_service.build_conversation_out(db, conversation, current_user.id)
  except messaging_service.CannotMessageSelfError:
    raise HTTPException(400, detail={"message": "Cannot message yourself", "field": "recipient_id"})
  except messaging_service.RecipientNotFoundError:
    raise HTTPException(404, detail={"message": "Recipient not found", "field": "recipient_id"})


@router.get("/unread-count", response_model=UnreadCountOut)
async def unread_count(
  db: AsyncSession = Depends(get_db),
  current_user: User = Depends(get_current_user),
  redis: Redis = Depends(get_redis),
):
  cache_key = f"conversations:unread:user={current_user.id}"

  cached = await cache_get(redis, cache_key)
  if cached is not None:
    return UnreadCountOut.model_validate(cached)

  total = await messaging_service.total_unread_count(db, current_user.id)
  data = UnreadCountOut(total=total).model_dump(mode="json")
  await cache_set(redis, cache_key, data, settings.cache_ttl_seconds)
  return UnreadCountOut.model_validate(data)


@router.get("/{conversation_id}", response_model=ConversationOut)
async def get_conversation(
  conversation_id: UUID,
  db: AsyncSession = Depends(get_db),
  current_user: User = Depends(get_current_user),
  redis: Redis = Depends(get_redis),
):
  cache_key = f"conversations:detail:user={current_user.id}:id={conversation_id}"

  cached = await cache_get(redis, cache_key)
  if cached is not None:
    return ConversationOut.model_validate(cached)
    
  try:
    conversation = await messaging_service.get_conversation_for_user(
      db, conversation_id, current_user.id,
    )
    conversation_out = await messaging_service.build_conversation_out(
      db, conversation, current_user.id,
    )
    await cache_set(
      redis,
      cache_key,
      conversation_out.model_dump(mode="json"),
      settings.cache_ttl_seconds,
    )
    return conversation_out
  except messaging_service.ConversationNotFoundError:
    raise HTTPException(404, detail={"message": "Conversation not found"})
  except messaging_service.ConversationAccessDeniedError:
    raise HTTPException(403, detail={"message": "Access denied"})


@router.get("/{conversation_id}/messages", response_model=list[MessageOut])
async def get_messages(
  conversation_id: UUID,
  before: UUID | None = None,
  limit: int = 50,
  db: AsyncSession = Depends(get_db),
  current_user: User = Depends(get_current_user),
  redis: Redis = Depends(get_redis),
):
  try:
    await messaging_service.get_conversation_for_user(
      db, conversation_id, current_user.id,
    )
  except messaging_service.ConversationNotFoundError:
    raise HTTPException(404, detail={"message": "Conversation not found"})
  except messaging_service.ConversationAccessDeniedError:
    raise HTTPException(403, detail={"message": "Access denied"})

  cache_key = (
    f"conversations:{conversation_id}:messages:"
    f"before={before or ''}:limit={limit}"
  )

  cached = await cache_get(redis, cache_key)
  if cached is not None:
    return [MessageOut.model_validate(item) for item in cached]

  messages = await messaging_service.list_messages(
    db, conversation_id, before, limit,
  )
  data = [MessageOut.model_validate(m).model_dump(mode="json") for m in messages]
  await cache_set(redis, cache_key, data, settings.cache_ttl_seconds)
  return [MessageOut.model_validate(item) for item in data]


@router.post("/{conversation_id}/messages", response_model=MessageOut, status_code=201)
async def send_message(
  conversation_id: UUID,
  data: MessageCreate,
  db: AsyncSession = Depends(get_db),
  current_user: User = Depends(get_current_user),
  redis: Redis = Depends(get_redis),
):
  try:
    message = await messaging_service.send_message(
      db, conversation_id, current_user.id, data.body
    )
    conversation = await messaging_service.get_conversation_for_user(
      db, conversation_id, current_user.id
    )

    await messaging_service.invalidate_for_both_participants(
      redis,
      conversation.user1_id,
      conversation.user2_id,
      conversation_id=conversation_id,
    )

    recipient = messaging_service.conversation_participant(
      conversation, current_user.id
    )
    await dispatch.notify.messages.received(
      conversation_id=conversation_id,
      recipient_id=recipient.id,
      sender_username=current_user.username,
      body=message.body,
    )
    return message
  except messaging_service.EmptyMessageBodyError:
    raise HTTPException(400, detail={"message": "Message body cannot be empty"})
  except messaging_service.ConversationNotFoundError:
    raise HTTPException(404, detail={"message": "Conversation not found"})
  except messaging_service.ConversationAccessDeniedError:
    raise HTTPException(403, detail={"message": "Access denied"})


@router.post("/{conversation_id}/read", status_code=204)
async def mark_read(
  conversation_id: UUID,
  db: AsyncSession = Depends(get_db),
  current_user: User = Depends(get_current_user),
  redis: Redis = Depends(get_redis),
):
  try:
    await messaging_service.mark_as_read(db, conversation_id, current_user.id)
    await messaging_service.invalidate_user_unread_count(redis, current_user.id)
    await messaging_service.invalidate_user_conversations(redis, current_user.id)
    await messaging_service.invalidate_conversation_detail(
      redis, conversation_id, current_user.id,
    )
  except messaging_service.ConversationNotFoundError:
    raise HTTPException(404, detail={"message": "Conversation not found"})
  except messaging_service.ConversationAccessDeniedError:
    raise HTTPException(403, detail={"message": "Access denied"})


@router.delete("/{conversation_id}/soft_delete_message", status_code=204, summary="soft_delete_message")
async def soft_delete_message(
  conversation_id: UUID,
  message_id: UUID,
  db: AsyncSession = Depends(get_db),
  current_user: User = Depends(get_current_user),
  redis: Redis = Depends(get_redis),
):
  try:
    conversation = await messaging_service.get_conversation_for_user(
      db, conversation_id, current_user.id,
    )

    await messaging_service.soft_delete_message(
      db, message_id, current_user.id, conversation_id,
    )

    await messaging_service.invalidate_for_both_participants(
      redis, conversation.user1_id, conversation.user2_id, conversation_id,
    )
  except messaging_service.ConversationNotFoundError:
    raise HTTPException(404, detail={"message": "Conversation not found"})
  except messaging_service.ConversationAccessDeniedError:
    raise HTTPException(403, detail={"message": "Access denied"})
  except messaging_service.MessageNotFoundError:
    raise HTTPException(404, detail={"message": "Message not found"})