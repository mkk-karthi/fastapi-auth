from datetime import datetime, timedelta, timezone
from typing import Any
import jwt
from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher

from app.core.config import settings


hasher = PasswordHash((BcryptHasher(),))


def hashPassword(password: str):
    return hasher.hash(password)


def verifyPassword(password: str, hash_password: str):
    return hasher.verify(password, hash_password)


def createAccessToken(data: Any):
    expiry = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE
    )
    token = jwt.encode(
        {"exp": expiry, "sub": str(data)},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return token


def verifyToken(token: str):
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
