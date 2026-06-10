from fastapi import APIRouter, Depends, HTTPException
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..dependencies import get_current_user
from ..models.user import User
from ..models.event import Event
from ..schemas.event import EventCreate, EventUpdate, EventOut
from ..schemas.registration import RegistrationOut, ParticipantOut
from ..services import events as events_service
from ..services import registrations as registration_service

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/", response_model=EventOut, status_code=201)
async def create_event(
  event_data: EventCreate,
  db: AsyncSession = Depends(get_db),
  current_user: User = Depends(get_current_user),
):
  return await events_service.create_event(event_data, db, current_user.id)


@router.get("/events", response_model=list[EventOut])
async def get_events(
  db: AsyncSession = Depends(get_db),
  current_user: User = Depends(get_current_user)
):
  result = await db.execute(select(Event).where(Event.creator_id == current_user.id))

  events = result.scalars().all()

  return events


@router.post("/{event_id}/join", response_model=RegistrationOut, status_code=201)
async def join_event(
  event_id: int,
  db: AsyncSession = Depends(get_db),
  current_user: User = Depends(get_current_user)
):
  try:
    return await registration_service.join_event(
      db,
      event_id=event_id,
      user_id=current_user.id
    )
  except registration_service.EventNotFoundError as e:
    raise HTTPException(status_code=404, detail=str(e))
  except registration_service.EventCreatorCannotJoinError as e:
    raise HTTPException(status_code=409, detail=str(e))
  except registration_service.EventAlreadyStartedError as e:
    raise HTTPException(status_code=409, detail=str(e))
  except registration_service.AlreadyRegisteredError as e:
    raise HTTPException(status_code=409, detail=str(e))
  except registration_service.EventFullError as e:
    raise HTTPException(status_code=409, detail=str(e))


@router.get("/{event_id}/participants", response_model=list[ParticipantOut])
async def get_participants(
  event_id: int,
  db: AsyncSession = Depends(get_db),
):
  try:
    registrations = await registration_service.get_event_participants(
      db,
      event_id=event_id,
    )
  except registration_service.EventNotFoundError as e:
    raise HTTPException(status_code=404, detail=str(e))

  return [
    ParticipantOut(user=reg.user, registered_at=reg.registered_at)
    for reg in registrations
  ]
