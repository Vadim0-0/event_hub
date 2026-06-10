from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
import bcrypt

from .config import settings


class InvalidTokenError(Exception):
  pass


# comparison of the entered password
def verify_password(plain_password: str, hashed_password: str) -> bool:
  return bcrypt.checkpw(
    plain_password.encode("utf-8"),
    hashed_password.encode("utf-8"),
  )


# password hashing
def get_password_hash(password: str) -> str:
  return bcrypt.hashpw(
    password.encode("utf-8"),
    bcrypt.gensalt(),
  ).decode("utf-8")


def create_access_token(
  *,
  subject: str | int,
  expires_delta: timedelta | None = None,
) -> str:
  expire = datetime.now(timezone.utc) + (
    expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
  )

  payload = {
    "sub": str(subject), 
    "exp": expire,
  }
  return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> int:
  try:
    payload = jwt.decode(
      token,
      settings.secret_key,
      algorithms=[settings.algorithm],
    )
    sub = payload.get("sub")
    if sub is None:
      raise InvalidTokenError()
    return int(sub)
  except (JWTError, ValueError):
    raise InvalidTokenError()