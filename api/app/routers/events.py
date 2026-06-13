from fastapi import APIRouter, Depends, HTTPException
from redis.asyncio import Redis
from sqlalchemy import func, select
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


@router.post("/", response_model=EventOut, status_code=201, summary="Creating new event")
async def create_event(
    event_data: EventCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
  ):
  """
    Creating event.
    Requires authentication.
  """

  return await events_service.create_event(event_data, db, current_user.id)


@router.get("/", response_model=list[EventOut], summary="Get events")
async def list_events(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
  ):
  """ Get list of upcoming events """

  return await events_service.list_events(db, skip=skip, limit=limit)


@router.get("/my", response_model=list[EventOut], summary="Get user events")
async def get_user_events(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
  ):
  """
    Get list of events created by the current user
  """
  return await events_service.get_user_events(db, user_id=current_user.id, skip=skip, limit=limit)


@router.get("/{event_id}", response_model=EventOut, summary="Get event by ID")
async def get_event(
  event_id: int,
  db: AsyncSession = Depends(get_db),
):

  """
    Get event by ID
  """

  try:
    return await events_service.get_event_by_id(db, event_id)
  except events_service.EventNotFoundError as e:
    raise HTTPException(status_code=404, detail=str(e))


@router.post("/{event_id}/join", response_model=RegistrationOut, status_code=201, summary='Registration for the event')
async def join_event(
  event_id: int,
  db: AsyncSession = Depends(get_db),
  current_user: User = Depends(get_current_user)
):
  """
    Registration for the event
  """

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


@router.get("/{event_id}/participants", response_model=list[ParticipantOut], summary="Get a list of event participants")
async def get_participants(
  event_id: int,
  db: AsyncSession = Depends(get_db),
  skip: int = 0,
  limit: int = 100
):
  """
    Get a list of event participants
  """

  try:
    registrations = await registration_service.get_event_participants(
      db,
      event_id=event_id,
      skip=skip,
      limit=limit
    )
  except registration_service.EventNotFoundError as e:
    raise HTTPException(status_code=404, detail=str(e))

  return [
    ParticipantOut(user=reg.user, registered_at=reg.registered_at)
    for reg in registrations
  ]


@router.patch("/{event_id}", response_model=EventOut, summary="Update event")
async def update_event(
  event_id: int,
  event_data: EventUpdate,
  db: AsyncSession = Depends(get_db),
  current_user: User = Depends(get_current_user),
):
  """
    Update event
  """

  try:
    return await events_service.update_event(
      event_data=event_data,
      event_id=event_id,
      db=db,
      user_id=current_user.id
    )
  except events_service.EventNotFoundError as e:
      raise HTTPException(status_code=404, detail=str(e))
  except events_service.PermissionDeniedError as e:
      raise HTTPException(status_code=403, detail=str(e)) 


@router.delete("/{event_id}", status_code=204, summary="Delete event")
async def delete_event(
  event_id: int,
  db: AsyncSession = Depends(get_db),
  current_user: User = Depends(get_current_user),
):
  """
    Delete event
  """

  try:
    await events_service.delete_event(
      db=db,
      event_id=event_id,
      user_id=current_user.id
    )
  except events_service.EventNotFoundError as e:
      raise HTTPException(status_code=404, detail=str(e))
  except events_service.PermissionDeniedError as e:
      raise HTTPException(status_code=403, detail=str(e)) 