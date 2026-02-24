from typing import Annotated

from app.core.auth import verifyToken
from fastapi import Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import GetDB, get_db
from app.models.user import User
from app.schemas.user import UserResponse
from app.services import user_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def get_current_user(db: GetDB, token: str = Depends(oauth2_scheme)):
    try:
        if not token:
            raise HTTPException(status_code=401, detail="Unauthorised")

        payload = verifyToken(token)
        id = payload.get("sub")

        user = user_service.get_user(db, id)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")

        else:
            user = jsonable_encoder(UserResponse.model_validate(user))
            return user

    except:
        raise HTTPException(status_code=401, detail="Invalid token")


CurrentUser = Annotated[User, Depends(get_current_user)]
