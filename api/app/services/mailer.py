import asyncio
import logging
import smtplib
from email.message import EmailMessage

from ..config import settings

logger = logging.getLogger(__name__)

def _send_sync(to: str, subject: str, body: str) -> None:
  msg = EmailMessage()
  msg["From"] = settings.smtp_from_email
  msg["To"] = to
  msg["Subject"] = subject
  msg.set_content(body)

  with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
    if settings.smtp_use_tls:
      smtp.starttls()
    if settings.smtp_user and settings.smtp_password:
      smtp.login(settings.smtp_user, settings.smtp_password)
    smtp.send_message(msg)


async def deliver_email(to: str, subject: str, body: str) -> None:
  if not settings.smtp_host:
    logger.info("EMAIL (dry-run) to=%s subject=%s body=%s", to, subject, body)
    return

  await asyncio.to_thread(_send_sync, to, subject, body)