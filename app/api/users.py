from typing import Union
from fastapi import APIRouter, UploadFile
from fastapi.encoders import jsonable_encoder

from app.core.database import SessionDep
from app.core.response import error_response, success_response
from app.schemas.response import (
    CommonResponse,
    ErrorResponse,
    PaginationMeta,
    SuccessResponse,
    ValidationErrorResponse,
)
from app.schemas.user import UserCreate, UserResponse, UserUpdate
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
    db: SessionDep,
    page: int = 1,
    size: int = 10,
):
    users = user_service.get_users(db, page, size)

    if not users.items:
        return error_response("User not found", 404)
    else:
        return success_response(data=users, message="Users fetched successfully")


@router.post("/", response_model=CommonResponse)
async def create_user(user: UserCreate, db: SessionDep):

    if user_service.email_exists(db, user.email):
        return error_response("Email already exist", 400)

    created = user_service.create_user(db, user)
    if not created:
        return error_response("User not created", 404)
    else:
        return success_response(
            data=jsonable_encoder(UserResponse.model_validate(created)),
            message="User created",
        )


@router.put("/{id}", response_model=CommonResponse)
def update_user(id: int, user: UserUpdate, db: SessionDep):
    updated = user_service.update_user(db, id, user)
    if not updated:
        return error_response("User not found", 404)
    else:
        return success_response(
            data=jsonable_encoder(UserResponse.model_validate(updated)),
            message="User updated",
        )


@router.get("/{id}", response_model=CommonResponse)
def get_user(id: int, db: SessionDep):
    user = user_service.get_user(db, id)
    if not user:
        return error_response("User not found", 404)
    else:
        return success_response(
            data=jsonable_encoder(UserResponse.model_validate(user)),
            message="User fetched successfully",
        )


@router.delete("/{id}", response_model=CommonResponse)
def delete_user(id: int, db: SessionDep):
    deleted = user_service.delete_user(db, id)
    if not deleted:
        return error_response("User not found", 404)
    else:
        return success_response(message="User deleted successfully")


@router.post("/upload-avatar/{id}", response_model=CommonResponse)
async def uploadAvatar(
    id: int,
    avatar: UploadFile,
    db: SessionDep,
):

    if not avatar or not avatar.filename:
        return error_response("Avatar is required", 422)

    uploaded = await user_service.upload_avatar(db, id, avatar)
    if not uploaded:
        return error_response("File not uploaded", 404)
    else:
        return success_response(
            data=jsonable_encoder(UserResponse.model_validate(uploaded)),
            message="File uploaded",
        )
