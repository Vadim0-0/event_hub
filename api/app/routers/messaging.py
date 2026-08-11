from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

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
):
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
  return ConversationsListOut(items=items, total=total)


@router.post("/", response_model=ConversationOut, status_code=201)
async def start_conversation(
  data: ConversationCreate,
  db: AsyncSession = Depends(get_db),
  current_user: User = Depends(get_current_user),
):
  try:
    conversation = await messaging_service.get_or_create_conversation(
      db, current_user.id, data.recipient_id
    )
  except messaging_service.CannotMessageSelfError:
    raise HTTPException(400, detail={"message": "Cannot message yourself", "field": "recipient_id"})
  except messaging_service.RecipientNotFoundError:
    raise HTTPException(404, detail={"message": "Recipient not found", "field": "recipient_id"})

  return await messaging_service.build_conversation_out(db, conversation, current_user.id)


@router.get("/unread-count", response_model=UnreadCountOut)
async def unread_count(
  db: AsyncSession = Depends(get_db),
  current_user: User = Depends(get_current_user),
):
  total = await messaging_service.total_unread_count(db, current_user.id)
  return UnreadCountOut(total=total)


@router.get("/{conversation_id}", response_model=ConversationOut)
async def get_conversation(
  conversation_id: UUID,
  db: AsyncSession = Depends(get_db),
  current_user: User = Depends(get_current_user),
):
  conversation = await messaging_service.get_conversation_for_user(
    db, conversation_id, current_user.id
  )
  await messaging_service.mark_as_read(db, conversation_id, current_user.id)
  return await messaging_service.build_conversation_out(db, conversation, current_user.id)


@router.get("/{conversation_id}/messages", response_model=list[MessageOut])
async def get_messages(
  conversation_id: UUID,
  before: UUID | None = None,
  limit: int = 50,
  db: AsyncSession = Depends(get_db),
  current_user: User = Depends(get_current_user),
):
  try:
    await messaging_service.get_conversation_for_user(db, conversation_id, current_user.id)
    return await messaging_service.list_messages(db, conversation_id, before, limit)
  except messaging_service.ConversationNotFoundError:
    raise HTTPException(404, detail={"message": "Conversation not found"})
  except messaging_service.ConversationAccessDeniedError:
    raise HTTPException(403, detail={"message": "Access denied"})


@router.post("/{conversation_id}/messages", response_model=MessageOut, status_code=201)
async def send_message(
  conversation_id: UUID,
  data: MessageCreate,
  db: AsyncSession = Depends(get_db),
  current_user: User = Depends(get_current_user),
):
  try:
    message = await messaging_service.send_message(
      db, conversation_id, current_user.id, data.body
    )
    conversation = await messaging_service.get_conversation_for_user(
      db, conversation_id, current_user.id
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
):
  try:
    await messaging_service.mark_as_read(db, conversation_id, current_user.id)
  except messaging_service.ConversationNotFoundError:
    raise HTTPException(404, detail={"message": "Conversation not found"})
  except messaging_service.ConversationAccessDeniedError:
    raise HTTPException(403, detail={"message": "Access denied"})


@router.delete("/{conversation_id}/soft_delete_message", status_code=204, summary="soft_delete_message")
async def soft_delete_message(
  conversation_id: UUID,
  db: AsyncSession = Depends(get_db),
  current_user: User = Depends(get_current_user),
):
  try:
    await messaging_service.soft_delete_message(db, conversation_id, current_user.id)
  except messaging_service.ConversationNotFoundError:
    raise HTTPException(404, detail={"message": "Conversation not found"})
  except messaging_service.ConversationAccessDeniedError:
    raise HTTPException(403, detail={"message": "Access denied"})