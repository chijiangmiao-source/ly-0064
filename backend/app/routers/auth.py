from datetime import timedelta
from litestar import Router, post, get
from litestar.controller import Controller
from litestar.di import Provide
from litestar.exceptions import NotAuthorizedException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import UserLogin, Token, UserResponse
from app.security import verify_password, create_access_token
from app.config import settings
from app.dependencies import get_current_user


class AuthController(Controller):
    path = "/auth"
    dependencies = {"db": Provide(get_db)}

    @post("/login")
    async def login(self, data: UserLogin, db: Session) -> Token:
        user = db.query(User).filter(User.username == data.username).first()
        if not user or not verify_password(data.password, user.password_hash):
            raise NotAuthorizedException("Invalid username or password")
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username, "user_id": user.id},
            expires_delta=access_token_expires
        )
        return Token(access_token=access_token)

    @get("/me", dependencies={"current_user": Provide(get_current_user)})
    async def get_me(self, current_user: User) -> UserResponse:
        return UserResponse.model_validate(current_user)
