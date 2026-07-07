from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_current_user
from ..database import get_db
from ..models.user import User
from ..schemas.user import UserRegister, UserLogin, Token, UserOut
from ..services import auth as auth_service

from ..worker.enqueue import enqueue_job

router = APIRouter(prefix="/auth", tags=["auth"])


# User registration
@router.post('/register', response_model=UserOut, status_code=201)
async def register(
  data: UserRegister, 
  db: AsyncSession = Depends(get_db),
):
  try:
    user = await auth_service.register_user(data, db)
  except auth_service.EmailAlreadyRegisteredError as e:
    raise HTTPException(
      status_code=409,
      detail={"message": str(e), "field": "email"},
    )
  except auth_service.UsernameAlreadyRegisteredError as e:
    raise HTTPException(
      status_code=409,
      detail={"message": str(e), "field": "username"},
    )

  await enqueue_job("send_welcome_email", user.id, user.email)
  return user


@router.post("/login", response_model=Token)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
  try:
    access_token = await auth_service.login(data, db)
  except auth_service.InvalidCredentialsError as e:
    raise HTTPException(status_code=401, detail=str(e))

  return Token(access_token=access_token)


# Getting the current user
@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)):
  return current_user