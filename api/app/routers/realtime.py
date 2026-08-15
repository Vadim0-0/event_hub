import asyncio
import contextlib
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from redis.asyncio import Redis

from ..config import settings
from ..redis_client import get_redis
from ..security import InvalidTokenError, decode_access_token
from ..realtime.publisher import user_channel

router = APIRouter(prefix="/realtime", tags=["realtime"])

async def _redis_to_ws(pubsub, websocket: WebSocket) -> None:
  async for message in pubsub.listen():
    if message["type"] != "message":
      continue
    await websocket.send_text(message["data"])


async def _ws_to_void(websocket: WebSocket) -> None:
  while True:
    await websocket.receive_text()


@router.websocket("/ws")
async def websocket_endpoint(
  websocket: WebSocket,
  token: str = Query(...),
):
  try:
    user_id = decode_access_token(token)
  except InvalidTokenError:
    await websocket.close(code=4401)
    return

  await websocket.accept()

  redis = Redis.from_url(settings.final_redis_url, decode_responses=True)
  pubsub = redis.pubsub()
  channel = user_channel(user_id)
  await pubsub.subscribe(channel)

  redis_task = asyncio.create_task(_redis_to_ws(pubsub, websocket))
  ws_task = asyncio.create_task(_ws_to_void(websocket))
  
  try:
    done, pending = await asyncio.wait(
      {redis_task, ws_task},
      return_when=asyncio.FIRST_COMPLETED,
    )
    for task in pending:
      task.cancel()
      with contextlib.suppress(asyncio.CancelledError):
        await task
  finally:
    await pubsub.unsubscribe(channel)
    await pubsub.aclose()
    await redis.aclose()