from uuid import UUID
from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import selectinload

from ...models.conversation import Conversation
from ...models.message import Message
from ...models.conversation_read import ConversationRead
from ...models.conversation_user_state import ConversationUserState
from ...models.message_user_hide import MessageUserHide
from ...models.user import User


async def get_conversation_user_state(db, conversation_id, user_id) -> ConversationUserState | None:
  return await db.get(
    ConversationUserState,
    {"conversation_id": conversation_id, "user_id": user_id},
  )


async def get_or_create_conversation_user_state(db, conversation_id, user_id) -> ConversationUserState:
  state = await get_conversation_user_state(db, conversation_id, user_id)
  if state:
    return state
  state = ConversationUserState(conversation_id=conversation_id, user_id=user_id)
  db.add(state)
  return state


async def get_hidden_message_ids(db, user_id: int) -> set[UUID]:
  result = await db.execute(
    select(MessageUserHide.message_id).where(MessageUserHide.user_id == user_id)
  )
  return set(result.scalars().all())


def visible_messages_conditions(
  conversation_id: UUID,
  user_id: int,
  cleared_at,
  hidden_message_ids: set[UUID],
):
  conditions = [
    Message.conversation_id == conversation_id,
    Message.is_deleted.is_(False),
  ]

  if cleared_at is not None:
    conditions.append(Message.created_at > cleared_at)

  if hidden_message_ids:
    conditions.append(Message.id.not_in(hidden_message_ids))

  return and_(*conditions)


def normalize_user_pair(user_a_id: int, user_b_id: int) -> tuple[int, int]:
  if user_a_id == user_b_id:
    raise ValueError("User cannot create conversation with themselves")

  return (min(user_a_id, user_b_id), max(user_a_id, user_b_id))


def user_is_participant(conversation: Conversation, user_id: int) -> bool:
  return user_id in (conversation.user1_id, conversation.user2_id)


def conversation_participant(conversation: Conversation, current_user_id: int) -> User:
  if not user_is_participant(conversation, current_user_id):
    raise ValueError("User is not a participant")

  return conversation.user1 if conversation.user1_id != current_user_id else conversation.user2


def recipient_id(conversation: Conversation, sender_id: int) -> int:
  return (
    conversation.user2_id
    if conversation.user1_id == sender_id
    else conversation.user1_id
  )


async def get_conversation_by_pair(db, user_a_id, user_b_id) -> Conversation | None:
  u1, u2 = normalize_user_pair(user_a_id, user_b_id)
  result = await db.execute(
    select(Conversation)
    .options(selectinload(Conversation.user1), selectinload(Conversation.user2))
    .where(Conversation.user1_id == u1, Conversation.user2_id == u2)
  )
  return result.scalar_one_or_none()


async def get_conversation_by_id(db, conversation_id: UUID) -> Conversation | None:
  result = await db.execute(
    select(Conversation)
    .options(selectinload(Conversation.user1), selectinload(Conversation.user2))
    .where(Conversation.id == conversation_id)
  )
  return result.scalar_one_or_none()


async def get_last_message(db, conversation_id: UUID, user_id: int) -> Message | None:
  state = await get_conversation_user_state(db, conversation_id, user_id)
  hidden_ids = await get_hidden_message_ids(db, user_id)

  result = await db.execute(
    select(Message)
    .where(visible_messages_conditions(
      conversation_id, user_id, state.cleared_at if state else None, hidden_ids
    ))
    .order_by(Message.created_at.desc())
    .limit(1)
  )
  return result.scalar_one_or_none()


async def count_unread(db, conversation_id, user_id) -> int:
  state = await get_conversation_user_state(db, conversation_id, user_id)
  if state and state.hidden_at is not None:
    return 0
  
  hidden_ids = await get_hidden_message_ids(db, user_id)
  cleared_at = state.cleared_at if state else None

  read = await db.get(ConversationRead, {"conversation_id": conversation_id, "user_id": user_id})
  last_read_at = read.last_read_at if read else None

  conditions = [
    visible_messages_conditions(conversation_id, user_id, cleared_at, hidden_ids),
    Message.sender_id != user_id,
  ]
  if last_read_at:
    conditions.append(Message.created_at > last_read_at)

  return await db.scalar(
    select(func.count()).select_from(Message).where(and_(*conditions))
  ) or 0


def build_conversation_list_where(user_id: int, search: str | None):
  hidden_conversations = (
    select(ConversationUserState.conversation_id)
    .where(
      ConversationUserState.user_id == user_id,
      ConversationUserState.hidden_at.isnot(None),
    )
    .scalar_subquery()
  )

  participant_filter = and_(
    or_(
      Conversation.user1_id == user_id,
      Conversation.user2_id == user_id,
    ),
    Conversation.id.not_in(hidden_conversations),
  )

  if not search or not search.strip():
    return participant_filter

  pattern = f"%{search.strip()}%"

  return and_(
    participant_filter,
    or_(
      and_(
        Conversation.user1_id == user_id,
        Conversation.user2.has(User.username.ilike(pattern)),
      ),
      and_(
        Conversation.user2_id == user_id,
        Conversation.user1.has(User.username.ilike(pattern)),
      ),
      Conversation.messages.any(
        and_(Message.body.ilike(pattern), Message.is_deleted.is_(False)),
      ),
    ),
  )


def users_without_visible_conversation_filter(current_user_id: int):
  visible_conversations = (
    select(
      func.coalesce(
        func.nullif(Conversation.user1_id, current_user_id),
        Conversation.user2_id,
      )
    )
    .outerjoin(
      ConversationUserState,
      and_(
        ConversationUserState.conversation_id == Conversation.id,
        ConversationUserState.user_id == current_user_id,
      ),
    )
    .where(
      or_(
        Conversation.user1_id == current_user_id,
        Conversation.user2_id == current_user_id,
      ),
      or_(
        ConversationUserState.hidden_at.is_(None),
        ConversationUserState.user_id.is_(None),
      ),
    )
    .scalar_subquery()
  )

  return and_(
    User.id != current_user_id,
    User.is_email_verified.is_(True),
    User.id.not_in(visible_conversations),
  )