import logging

from ..config import settings
from ..database import AsyncSessionLocal
from ..services.demo.simulator import run_demo_simulator_tick

logger = logging.getLogger(__name__)


async def demo_simulator_tick(ctx) -> str:
  if not settings.demo_simulator_enabled:
    return "disabled"

  async with AsyncSessionLocal() as db:
    result = await run_demo_simulator_tick(db)
    logger.info("Demo simulator tick: %s", result)
    return result