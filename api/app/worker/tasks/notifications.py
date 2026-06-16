import logging

logger = logging.getLogger(__name__)

async def send_email(to: str, subject: str, body: str) -> None:
  logger.info("EMAIL to=%s subject=%s body=%s", to, subject, body)