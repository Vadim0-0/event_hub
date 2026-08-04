from uuid import UUID
from collections.abc import Sequence
from sqlalchemy import func, select, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.event import Event
from ...models.registration import EventRegistration
from ...schemas.event import CreatorOut, EventCreate, EventOut, EventUpdate

from . import exceptions