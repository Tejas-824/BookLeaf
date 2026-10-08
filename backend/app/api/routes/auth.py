from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.errors import AppError
from app.core.security import create_access_token, verify_password
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == body.email.lower()))
    # same message for wrong email and wrong password (no user hints)
    if not user or not verify_password(body.password, user.password_hash):
        raise AppError(401, "invalid_credentials", "Incorrect email or password.")
    token = create_access_token(user.id, user.role)
    return TokenResponse(access_token=token, user_id=user.id, role=user.role, name=user.name)


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {"user_id": user.id, "name": user.name, "email": user.email, "role": user.role}