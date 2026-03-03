from fastapi import APIRouter, BackgroundTasks, Body, Depends, Request
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer
from pydantic import EmailStr
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.auth import createAccessToken, verifyPassword
from app.core.config import settings
from app.core.database import SessionDep
from app.core.helper import generateOtp
from app.core.mail import MailSchema, mailSend
from app.core.redis import RedisCacheDep
from app.core.response import error_response, success_response
from app.debs.auth import CurrentUser
from app.schemas.auth import (
    ChangePasswordSchema,
    LoginSchema,
    MailVerifyOTP,
    ResetPasswordSchema,
    SigninSchema,
)
from app.schemas.response import CommonResponse
from app.schemas.user import UserResponse, UserUpdate
from app.services import user_service


router = APIRouter(tags=["Auth"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/signin", response_model=CommonResponse)
@limiter.limit(settings.AUTH_MAX_RATELIMIT)
async def signin(
    request: Request,
    user: SigninSchema,
    background_tasks: BackgroundTasks,
    db: SessionDep,
    RedisCache=RedisCacheDep,
    otp: str = Depends(generateOtp),
):

    if user_service.email_exists(db, user.email):
        return error_response("Email already exist", 400)

    created = user_service.create_user(db, user)
    if not created:
        return error_response("User not created", 404)
    else:
        await RedisCache.set(created.email, otp, settings.OTP_EXPIRE)
        message = MailSchema(
            recipient=created.email,
            subject="Register Successful - FastAPI",
            body=f"<p>Hi <strong>{created.name}</strong>,</p><p style='color:blue; background: yellow;'>Welcome to fastAPI. Your OTP is <code>{otp}</code>.</p>",
        )

        background_tasks.add_task(mailSend, message)

        return success_response(
            data=jsonable_encoder(UserResponse.model_validate(created)),
            message="User registered",
        )


@router.post("/login", response_model=CommonResponse)
@limiter.limit(settings.AUTH_MAX_RATELIMIT)
async def login(request: Request, req: LoginSchema, db: SessionDep):
    user = user_service.get_user_by_mail(db, req.email)
    if not user:
        return error_response("Email & password incorrect")
    elif not user.mail_verified_at:
        return error_response("Email not verified")

    if verifyPassword(req.password, user.password):
        token = createAccessToken(user.id)
        user = jsonable_encoder(UserResponse.model_validate(user))
        return success_response(
            data={"user": user, "token": token}, message="Login success"
        )
    else:
        return error_response("Email & password incorrect")


@router.post("/verify-otp", response_model=CommonResponse)
async def verifyOTP(req: MailVerifyOTP, db: SessionDep, RedisCache=RedisCacheDep):
    otp = await RedisCache.get(req.email)
    if req.otp == otp:
        updated = user_service.update_verified_user(db, req.email)

        if not updated:
            return error_response("Mail not verified", 400)
        else:
            await RedisCache.delete(req.email)
            return success_response(message="Mail verified")

    else:
        return error_response("OTP is invalid", 400)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


@router.get("/profile", response_model=CommonResponse)
def get_current_user(current_user: CurrentUser):
    return success_response(data=current_user)


@router.post("/change-password", response_model=CommonResponse)
def change_password(
    req: ChangePasswordSchema, current_user: CurrentUser, db: SessionDep
):
    user = user_service.get_user_by_mail(db, current_user["email"])

    if verifyPassword(req.old_password, user.password):
        # check new password is currently used
        if verifyPassword(req.password, user.password):
            return error_response("Password has been previously used")

        user_service.update_user(
            db, current_user["id"], UserUpdate(name=user.name, password=req.password)
        )

        return success_response(message="Password updated")
    else:
        return error_response("Password is incorrect")


@router.post("/forgot-password", response_model=CommonResponse)
@limiter.limit(settings.AUTH_MAX_RATELIMIT)
async def forgot_password(
    request: Request,
    background_tasks: BackgroundTasks,
    db: SessionDep,
    email: EmailStr = Body(..., embed=True),
    RedisCache=RedisCacheDep,
    otp: str = Depends(generateOtp),
):
    user = user_service.get_user_by_mail(db, email)
    if user:
        await RedisCache.set(user.email, otp, settings.OTP_EXPIRE)
        message = MailSchema(
            recipient=user.email,
            subject="Forgot your password? - FastAPI",
            body=f"<p>Hi <strong>{user.name}</strong>,</p><p>We received a request to reset your password for your account. Your OTP is <code>{otp}</code>.</p><br><p style='color:red; background: yellow;'>Note: This OTP expires in {settings.OTP_EXPIRE} minutes. Don't share this OTP.</p>",
        )

        background_tasks.add_task(mailSend, message)

    return success_response(message="Reset password mail sended")


@router.post("/reset-password", response_model=CommonResponse)
async def reset_password(
    req: ResetPasswordSchema, db: SessionDep, RedisCache=RedisCacheDep
):
    user = user_service.get_user_by_mail(db, req.email)
    if user:

        otp = await RedisCache.get(req.email)
        if req.otp == otp:
            # check new password is currently used
            if verifyPassword(req.password, user.password):
                return error_response("Password has been previously used")

            user_service.update_user(
                db, user.id, UserUpdate(name=user.name, password=req.password)
            )
            await RedisCache.delete(req.email)
            return success_response(message="Password updated")

        else:
            return error_response("OTP is invalid", 400)

    else:
        return error_response("OTP is invalid", 400)
