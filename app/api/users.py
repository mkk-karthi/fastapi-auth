from typing import Union
from fastapi import APIRouter, BackgroundTasks, Depends, UploadFile
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.helper import generate_otp
from app.core.mail import MailSchema, mailSend
from app.core.redis import redisCache
from app.core.response import error_response, success_response
from app.schemas.response import (
    CommonResponse,
    ErrorResponse,
    PaginationMeta,
    SuccessResponse,
    ValidationErrorResponse,
)
from app.schemas.user import MailVerifyOTP, UserCreate, UserResponse, UserUpdate
from app.services import user_service


router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/",
    response_model=Union[
        SuccessResponse[PaginationMeta[UserResponse]],
        ValidationErrorResponse,
        ErrorResponse,
    ],
)
def get_users(
    page: int = 1,
    size: int = 10,
    db: Session = Depends(get_db),
):
    users = user_service.get_users(db, page, size)

    if not users.items:
        return error_response("User not found", 404)
    else:
        return success_response(data=users, message="Users fetched successfully")


@router.post("/", response_model=CommonResponse)
async def create_user(
    user: UserCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):

    if user_service.email_exists(db, user.email):
        return error_response("Email already exist", 404)

    created = user_service.create_user(db, user)
    if not created:
        return error_response("User not created", 404)
    else:
        otp = generate_otp()
        await redisCache.set(created.email, otp, settings.OTP_EXPIRY)
        message = MailSchema(
            recipient=created.email,
            subject="Register Successful - FastAPI",
            body=f"<p>Hai <strong>{created.name}</strong>,</p><p style='color:blue; background: yellow;'>Welcome to fastAPI. Your OTP is <code>{otp}</code>.</p>",
        )

        background_tasks.add_task(mailSend, message)

        return success_response(
            data=jsonable_encoder(UserResponse.model_validate(created)),
            message="User created",
        )


@router.put("/{id}", response_model=CommonResponse)
def update_user(id: int, user: UserUpdate, db: Session = Depends(get_db)):
    updated = user_service.update_user(db, id, user)
    if not updated:
        return error_response("User not found", 404)
    else:
        return success_response(
            data=jsonable_encoder(UserResponse.model_validate(updated)),
            message="User updated",
        )


@router.get("/{id}", response_model=CommonResponse)
def get_user(id: int, db: Session = Depends(get_db)):
    user = user_service.get_user(db, id)
    if not user:
        return error_response("User not found", 404)
    else:
        return success_response(
            data=jsonable_encoder(UserResponse.model_validate(user)),
            message="User fetched successfully",
        )


@router.delete("/{id}", response_model=CommonResponse)
def delete_user(id: int, db: Session = Depends(get_db)):
    deleted = user_service.delete_user(db, id)
    if not deleted:
        return error_response("User not found", 404)
    else:
        return success_response(message="User deleted successfully")


@router.post("/upload-avatar/{id}", response_model=CommonResponse)
async def uploadAvatar(
    id: int,
    avatar: UploadFile,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):

    if not avatar or not avatar.filename:
        return error_response("Avatar is required", 422)

    uploaded = await user_service.upload_avatar(db, id, avatar)
    if not uploaded:
        return error_response("File not uploaded", 404)
    else:
        message = MailSchema(
            recipient=uploaded.email,
            subject="Avatar Updated - FastAPI",
            body=f"<p>Hai <strong>{uploaded.name}</strong>,</p><p style='color:blue; background: yellow;'>Avatar update sucessfully.</p>",
            attachment=uploaded.avatar,
        )

        background_tasks.add_task(mailSend, message)

        return success_response(
            data=jsonable_encoder(UserResponse.model_validate(uploaded)),
            message="File uploaded",
        )


@router.post("/verify-otp", response_model=CommonResponse)
async def verifyOTP(user: MailVerifyOTP, db: Session = Depends(get_db)):
    otp = await redisCache.get(user.email)
    if user.otp == otp:
        updated = user_service.update_verified_user(db, user.email)

        if not updated:
            return error_response("Mail not verified", 400)
        else:
            await redisCache.delete(user.email)
            return success_response(message="Mail verified")

    else:
        return error_response("Mail not verified", 400)
