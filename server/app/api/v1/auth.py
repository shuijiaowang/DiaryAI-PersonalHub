from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import TokenPair, UserCreate, UserLogin, UserOut
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=UserOut, status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> User:
    return AuthService(db).register(payload)


@router.post("/login", response_model=TokenPair)
def login(payload: UserLogin, db: Session = Depends(get_db)) -> TokenPair:
    return AuthService(db).login(payload)


@router.post("/refresh", response_model=TokenPair)
def refresh(
    refresh_token: str = Body(..., embed=True),
    db: Session = Depends(get_db),
) -> TokenPair:
    return AuthService(db).refresh(refresh_token)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)) -> User:
    return user
