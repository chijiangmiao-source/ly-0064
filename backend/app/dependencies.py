from typing import Optional
from litestar import Request
from litestar.exceptions import NotAuthorizedException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.security import decode_token


def get_current_user(request: Request, db: Session = next(get_db())) -> User:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise NotAuthorizedException("Not authenticated")
    
    token = auth_header.split(" ")[1]
    payload = decode_token(token)
    username: str = payload.get("sub")
    if username is None:
        raise NotAuthorizedException("Invalid token")
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise NotAuthorizedException("User not found")
    
    return user


def get_current_admin_user(request: Request, db: Session = next(get_db())) -> User:
    user = get_current_user(request, db)
    if not user.is_admin:
        raise NotAuthorizedException("Not authorized as admin")
    return user
