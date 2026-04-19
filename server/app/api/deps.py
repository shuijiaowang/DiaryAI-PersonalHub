from collections.abc import Generator

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import TokenError, decode_token
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repo import UserRepository

DBSession = Generator[Session, None, None]


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="missing bearer token")
    token = authorization.split(" ", 1)[1]
    try:
        payload = decode_token(token, expected_type="access")
    except TokenError as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail=str(e)) from e

    user = UserRepository(db).get(int(payload["sub"]))
    if user is None or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="invalid user")
    return user
