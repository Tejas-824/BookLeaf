from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User

bearer = HTTPBearer(auto_error=False)


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    if not creds:
        raise AppError(401, "not_authenticated", "Please log in to continue.")
    payload = decode_token(creds.credentials)
    user = db.get(User, int(payload["sub"]))
    if not user:
        raise AppError(401, "invalid_token", "User no longer exists.")
    return user


def require_author(user: User = Depends(get_current_user)) -> User:
    if user.role != "author" or not user.author_id:
        raise AppError(403, "forbidden", "This action is only for authors.")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise AppError(403, "forbidden", "Admin access required.")
    return user