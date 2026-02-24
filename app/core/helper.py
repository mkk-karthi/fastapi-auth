from datetime import datetime
import os
import random
import string
from typing import Type, TypeVar
from fastapi import HTTPException, UploadFile
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Query

from app.core.config import settings

SchemaType = TypeVar("SchemaType", bound=BaseModel)


def pagination(
    query: Query, schema: Type[SchemaType] = None, page: int = 1, size: int = 10
):
    total = query.count()

    items = query.offset((page - 1) * size).limit(size).all()

    if schema:
        items = [schema.model_validate(item) for item in items]

    return {
        "items": jsonable_encoder(items),
        "page": page,
        "size": size,
        "total": total,
    }


UPLOAD_DIR = settings.UPLOAD_DIR
os.makedirs(UPLOAD_DIR, exist_ok=True)


async def uploadFile(file: UploadFile) -> str:
    MAX_FILE_SIZE = settings.MAX_FILE_SIZE * 1024 * 1024  # 5MB
    ALLOWED_TYPES = ["image/jpeg", "image/png"]

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, "Invalid file type")

    contents = await file.read()

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large")

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_path = os.path.join(UPLOAD_DIR, f"{timestamp}_{file.filename}")

    with open(file_path, "wb") as f:
        f.write(contents)

    return file_path


def deleteFile(path: str):
    if os.path.exists(path):
        print(path)
        os.unlink(path)


def generateOtp(length: int = settings.OTP_LENGTH) -> str:
    return "".join(random.choices(string.digits, k=length))
