from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.user import User


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
  result = await db.execute(select(User).where(User.email == email))
  return result.scalar_one_or_none()


async def is_username_taken(db: AsyncSession, username: str) -> bool:
    result = await db.scalar(
        select(User.id).where(User.username == username)
    )
    return result is not None