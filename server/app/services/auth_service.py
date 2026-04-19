from sqlalchemy.orm import Session

from app.core.errors import Conflict, Unauthorized
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.user import TokenPair, UserCreate, UserLogin


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserRepository(db)

    def register(self, payload: UserCreate) -> User:
        if self.users.get_by_username(payload.username):
            raise Conflict("username already exists")
        if payload.email and self.users.get_by_email(payload.email):
            raise Conflict("email already exists")
        user = User(
            username=payload.username,
            email=payload.email,
            password_hash=hash_password(payload.password),
        )
        self.users.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def login(self, payload: UserLogin) -> TokenPair:
        user = self.users.get_by_username(payload.username)
        if not user or not verify_password(payload.password, user.password_hash):
            raise Unauthorized("invalid username or password")
        if not user.is_active:
            raise Unauthorized("user disabled")
        return TokenPair(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
        )

    def refresh(self, refresh_token: str) -> TokenPair:
        payload = decode_token(refresh_token, expected_type="refresh")
        sub = int(payload["sub"])
        return TokenPair(
            access_token=create_access_token(sub),
            refresh_token=create_refresh_token(sub),
        )
