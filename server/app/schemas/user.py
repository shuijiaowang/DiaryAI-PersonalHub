from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.common import TimestampedOut


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=128)
    email: EmailStr | None = None

    @field_validator("password")
    @classmethod
    def password_utf8_byte_limit(cls, v: str) -> str:
        if len(v.encode("utf-8")) > 72:
            raise ValueError("password must be at most 72 bytes in UTF-8 (bcrypt limit)")
        return v


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(TimestampedOut):
    username: str
    email: str | None
    is_active: bool


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
