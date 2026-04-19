from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings


def hash_password(plain: str) -> str:
    digest = plain.encode("utf-8")
    hashed = bcrypt.hashpw(digest, bcrypt.gensalt())
    return hashed.decode("ascii")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("ascii"))
    except ValueError:
        return False


def _create_token(subject: str, expires_delta: timedelta, token_type: str) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
        "type": token_type,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_access_token(subject: str | int) -> str:
    return _create_token(
        str(subject), timedelta(minutes=settings.JWT_ACCESS_EXPIRE_MIN), "access"
    )


def create_refresh_token(subject: str | int) -> str:
    return _create_token(
        str(subject), timedelta(days=settings.JWT_REFRESH_EXPIRE_DAYS), "refresh"
    )


class TokenError(Exception):
    pass


def decode_token(token: str, expected_type: str = "access") -> dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError as e:
        raise TokenError(f"invalid token: {e}") from e
    if payload.get("type") != expected_type:
        raise TokenError(f"unexpected token type: {payload.get('type')}")
    return payload
