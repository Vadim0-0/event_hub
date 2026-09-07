import json
import logging

from pywebpush import WebPushException, webpush
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...config import settings
from ...models.push_subscription import PushSubscription
from ...schemas.push import PushSubscribeIn

logger = logging.getLogger(__name__)


async def upsert_subscription(
  db: AsyncSession,
  *,
  user_id: int,
  data: PushSubscribeIn,
  user_agent: str | None = None,
) -> PushSubscription:
  result = await db.execute(
    select(PushSubscription).where(PushSubscription.endpoint == data.endpoint)
  )
  existing = result.scalar_one_or_none()

  if existing is None:
    existing = PushSubscription(
      user_id=user_id,
      endpoint=data.endpoint,
      p256dh=data.keys.p256dh,
      auth=data.keys.auth,
      user_agent=user_agent,
    )
    db.add(existing)
  else:
    existing.user_id = user_id
    existing.p256dh = data.keys.p256dh
    existing.auth = data.keys.auth
    existing.user_agent = user_agent

  await db.commit()
  await db.refresh(existing)
  return existing


async def remove_subscription(
  db: AsyncSession,
  *,
  user_id: int,
  endpoint: str,
) -> None:
  result = await db.execute(
    select(PushSubscription).where(
      PushSubscription.user_id == user_id,
      PushSubscription.endpoint == endpoint,
    )
  )
  sub = result.scalar_one_or_none()
  if sub is None:
    return

  await db.delete(sub)
  await db.commit()


async def get_user_subscriptions(
  db: AsyncSession,
  user_id: int,
) -> list[PushSubscription]:
  result = await db.execute(
    select(PushSubscription).where(PushSubscription.user_id == user_id)
  )
  return list(result.scalars().all())


async def delete_subscription_by_id(db: AsyncSession, subscription_id: int) -> None:
  sub = await db.get(PushSubscription, subscription_id)
  if sub is None:
    return
  await db.delete(sub)
  await db.commit()


def send_web_push(
  *,
  subscription: PushSubscription,
  title: str,
  body: str,
  url: str,
  tag: str,
  private_key: str | None = None,
) -> None:
  payload = json.dumps({
    "title": title,
    "body": body,
    "url": url,
    "tag": tag,
  })

  webpush(
    subscription_info={
      "endpoint": subscription.endpoint,
      "keys": {
        "p256dh": subscription.p256dh,
        "auth": subscription.auth,
      },
    },
    data=payload,
    vapid_private_key=private_key or settings.vapid_private_key,
    vapid_claims={"sub": settings.vapid_subject},
  )


async def send_to_user(
  db: AsyncSession,
  *,
  user_id: int,
  title: str,
  body: str,
  url: str,
  tag: str,
) -> None:
  if not settings.push_enabled:
    return

  subscriptions = await get_user_subscriptions(db, user_id)
  private_key = settings.vapid_private_key
  if not private_key:
    logger.warning("Push skipped user=%s: VAPID private key is not configured", user_id)
    return

  for sub in subscriptions:
    try:
      send_web_push(
        subscription=sub,
        title=title,
        body=body,
        url=url,
        tag=tag,
        private_key=private_key,
      )
      logger.info("Push sent user=%s subscription=%s", user_id, sub.id)
    except WebPushException as exc:
      status = getattr(getattr(exc, "response", None), "status_code", None)
      logger.warning(
        "Push failed user=%s status=%s endpoint=%s error=%s",
        user_id,
        status,
        sub.endpoint,
        exc,
      )
      if status == 410:
        await delete_subscription_by_id(db, sub.id)
    except ValueError as exc:
      logger.error("Push configuration error user=%s: %s", user_id, exc)
      return