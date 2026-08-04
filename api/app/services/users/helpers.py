from sqlalchemy import func, or_

from ...models.event import Event
from ...models.user import User


def apply_user_search(query, search: str | None):
  if not search:
    return query

  pattern = f"%{search.strip()}%"
  return query.where(
    or_(
      User.username.ilike(pattern),
      User.email.ilike(pattern),
    )
  )


def apply_event_search(query, search: str | None):
  if not search:
    return query

  pattern = f"%{search.strip()}%"
  return query.where(
    or_(
      Event.title.ilike(pattern),
      Event.description.ilike(pattern),
    )
  )


def verified_users_only(query):
  return query.where(User.is_email_verified.is_(True))