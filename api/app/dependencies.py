# JWT authentication in FastAPI

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .database import get_db
from .models.user import User
from .security import decode_access_token, InvalidTokenError

security = HTTPBearer()


async def get_current_user(
  credentials: HTTPAuthorizationCredentials = Depends(security),
  db: AsyncSession = Depends(get_db),
) -> User:
  try:
    user_id = decode_access_token(credentials.credentials)
  except InvalidTokenError:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Invalid token",
      headers={"WWW-Authenticate": "Bearer"},
    )

  result = await db.execute(select(User).where(User.id == user_id))
  user = result.scalar_one_or_none()

  if user is None:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="User not found",
    )

  return user
