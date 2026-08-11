from datetime import datetime, timezone

from sqlalchemy import select, func, or_, and_, update
from sqlalchemy.orm import selectinload

from ...models.conversation import Conversation
from ...models.message import Message
from ...models.conversation_read import ConversationRead
from ...models.user import User

from ...schemas.messaging import ConversationOut, ConversationParticipantOut, MessageOut

from . import helpers
from . import exceptions


async def get_or_create_conversation(db, current_user_id, recipient_id) -> Conversation:
  if current_user_id == recipient_id:
    raise exceptions.CannotMessageSelfError()

  recipient = await db.get(User, recipient_id)
  if not recipient or not recipient.is_email_verified:
    raise exceptions.RecipientNotFoundError()

  existing = await helpers.get_conversation_by_pair(db, current_user_id, recipient_id)
  if existing:
    return existing
    
  u1, u2 = helpers.normalize_user_pair(current_user_id, recipient_id)
  conversation = Conversation(user1_id=u1, user2_id=u2)
  db.add(conversation)

  try:
    await db.commit()
  except exceptions.IntegrityError:
    await db.rollback()
    
    existing = await helpers.get_conversation_by_pair(db, current_user_id, recipient_id)
    if existing:
      return existing
    
    raise exceptions.ConversationCreationError("Failed to create conversation")


  await db.commit()
  await db.refresh(conversation, ["user1", "user2"])
  return conversation


async def get_conversation_for_user(db, conversation_id, user_id) -> Conversation:
  conversation = await helpers.get_conversation_by_id(db, conversation_id)
  if not conversation:
    raise exceptions.ConversationNotFoundError()
  if not helpers.user_is_participant(conversation, user_id):
    raise exceptions.ConversationAccessDeniedError()
  return conversation


async def send_message(db, conversation_id, sender_id, body) -> Message:
  conversation = await get_conversation_for_user(db, conversation_id, sender_id)

  text = body.strip()
  if not text:
    raise exceptions.EmptyMessageBodyError()

  message = Message(
    conversation_id=conversation.id,
    sender_id=sender_id,
    body=text,
  )

  conversation = await get_conversation_for_user(db, conversation_id, sender_id)

  await db.execute(
    update(Conversation)
    .where(Conversation.id == conversation.id)
    .values(updated_at=func.now())
  )

  db.add(message)
  await db.commit()
  await db.refresh(message)
  return message


async def mark_as_read(db, conversation_id, user_id) -> None:
  await get_conversation_for_user(db, conversation_id, user_id)

  read = await db.get(ConversationRead, {"conversation_id": conversation_id, "user_id": user_id})
  now = datetime.now(timezone.utc)

  if read:
    read.last_read_at = now
  else:
    db.add(ConversationRead(conversation_id=conversation_id, user_id=user_id, last_read_at=now))

  await db.commit()


async def soft_delete_message(db, message_id, user_id) -> Message:
  message = await db.get(Message, message_id)
  if not message:
    raise exceptions.MessageNotFoundError()
  if message.sender_id != user_id:
    raise exceptions.ConversationAccessDeniedError()

  message.is_deleted = True
  await db.commit()
  await db.refresh(message)
  return message


async def build_conversation_out(db, conversation, current_user_id) -> ConversationOut:
  participant = helpers.conversation_participant(conversation, current_user_id)
  last_message = await helpers.get_last_message(db, conversation.id)
  unread = await helpers.count_unread(db, conversation.id, current_user_id)

  return ConversationOut(
    id=conversation.id,
    participant=ConversationParticipantOut(id=participant.id, username=participant.username),
    last_message=MessageOut.model_validate(last_message) if last_message else None,
    unread_count=unread,
    updated_at=conversation.updated_at,
  )


async def list_user_conversations(
  db,
  user_id: int,
  skip: int,
  limit: int,
  search: str | None = None,
):
  participant_filter = or_(
    Conversation.user1_id == user_id,
    Conversation.user2_id == user_id,
  )

  where_clause = helpers.build_conversation_list_where(user_id, search)

  total = await db.scalar(
    select(func.count()).select_from(Conversation).where(where_clause)
  )

  result = await db.execute(
    select(Conversation)
    .options(selectinload(Conversation.user1), selectinload(Conversation.user2))
    .where(where_clause)
    .order_by(Conversation.updated_at.desc())
    .offset(skip)
    .limit(limit)
  )
  return result.scalars().all(), total


async def list_messages(db, conversation_id, before_id=None, limit=50):
  query = (
    select(Message)
    .where(Message.conversation_id == conversation_id, Message.is_deleted.is_(False))
    .order_by(Message.created_at.desc())
    .limit(limit)
  )
  if before_id:
    sub = select(Message.created_at).where(Message.id == before_id).scalar_subquery()
    query = query.where(Message.created_at < sub)

  result = await db.execute(query)
  return list(reversed(result.scalars().all()))


async def total_unread_count(db, user_id: int) -> int:
  result = await db.execute(
    select(Conversation.id).where(
      or_(Conversation.user1_id == user_id, Conversation.user2_id == user_id)
    )
  )
  total = 0
  for conversation_id in result.scalars():
    total += await helpers.count_unread(db, conversation_id, user_id)
  return total