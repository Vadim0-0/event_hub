from fastapi import APIRouter, Depends, HTTPException
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_current_user
from ..database import get_db
from ..models.user import User
from ..redis_client import get_redis
from ..schemas.user import (
  UserRegister,
  UserLogin,
  Token,
  UserOut,
  RegisterPendingOut,
  VerifyEmailIn,
  VerifyEmailOut,
  ResendVerificationIn,
)
from ..services import auth as auth_service
from ..services import email_verification
from ..notifications import dispatch

router = APIRouter(prefix="/auth", tags=["auth"])


# User registration
@router.post("/register", response_model=RegisterPendingOut, status_code=201)
async def register(
  data: UserRegister, 
  db: AsyncSession = Depends(get_db),
  redis: Redis = Depends(get_redis),
):
  try:
    user, code = await auth_service.register_user(data, db, redis)
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

  await dispatch.notify.auth.verification_code(user.id, user.email, code)
  
  return RegisterPendingOut(
    message="Verification code sent to your email",
    email=user.email,
  )


@router.post("/verify-email", response_model=VerifyEmailOut)
async def verify_email(
  data: VerifyEmailIn,
  db: AsyncSession = Depends(get_db),
  redis: Redis = Depends(get_redis),
):
  try:
    user, access_token = await auth_service.verify_email(
      data.email,
      data.code,
      db,
      redis,
    )
  except auth_service.UserNotFoundForVerificationError as e:
    raise HTTPException(status_code=404, detail=str(e))
  except auth_service.EmailAlreadyVerifiedError as e:
    raise HTTPException(status_code=409, detail=str(e))
  except auth_service.InvalidVerificationCodeError as e:
    raise HTTPException(status_code=400, detail=str(e))

  await dispatch.notify.auth.welcome(user.id, user.email, user.username)

  return VerifyEmailOut(
    user=UserOut.model_validate(user),
    access_token=access_token,
  )


@router.post("/resend-verification-code", response_model=RegisterPendingOut)
async def resend_verification_code(
  data: ResendVerificationIn,
  db: AsyncSession = Depends(get_db),
  redis: Redis = Depends(get_redis),
):
  try:
    user, code = await auth_service.resend_verification_code(data.email, db, redis)
  except email_verification.ResendTooSoonError as e:
    raise HTTPException(
      status_code=429,
      detail={
        "message": str(e),
        "retry_after": e.retry_after,
      },
      headers={"Retry-After": str(e.retry_after)},
    )

  if user is not None and code is not None:
    await dispatch.notify.auth.verification_code(user.id, user.email, code)

  return RegisterPendingOut(
    message="If the account exists and is not verified, a new code was sent",
    email=data.email,
  )


@router.post("/login", response_model=Token)
async def login(
  data: UserLogin, 
  db: AsyncSession = Depends(get_db)
):
  try:
    user, access_token = await auth_service.login(data, db)
  except auth_service.InvalidCredentialsError as e:
    raise HTTPException(status_code=401, detail=str(e))
  except auth_service.EmailNotVerifiedError as e:
    raise HTTPException(status_code=403, detail=str(e))
  
  await dispatch.notify.auth.login(user.id, user.email, user.username)

  return Token(access_token=access_token)


# Getting the current user
@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)):
  return current_user