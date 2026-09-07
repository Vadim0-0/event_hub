import logging

from ..database import AsyncSessionLocal
from ..services.demo.data import is_demo_email
from ..services.push import services as push_service
from ..models.user import User

logger = logging.getLogger(__name__)


async def send_to_user(
  *,
  user_id: int,
  title: str,
  body: str,
  url: str,
  tag: str,
) -> None:
  async with AsyncSessionLocal() as db:
    user = await db.get(User, user_id)
    if user is None or user.is_demo or is_demo_email(user.email):
      return

    await push_service.send_to_user(
      db,
      user_id=user_id,
      title=title,
      body=body,
      url=url,
      tag=tag,
    )