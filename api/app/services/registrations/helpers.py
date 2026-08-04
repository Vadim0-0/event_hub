from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from sqlalchemy.orm import selectinload

from ...models.event import Event
from ...models.registration import EventRegistration