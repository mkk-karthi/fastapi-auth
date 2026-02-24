from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.auth import createAccessToken, verifyPassword
from app.core.config import settings
from app.core.database import get_db
from app.core.helper import generateOtp
from app.core.mail import MailSchema, mailSend
from app.core.redis import redisCache
from app.core.response import error_response, success_response
from app.debs.auth import CurrentUser
from app.schemas.auth import LoginSchema
from app.schemas.response import CommonResponse
from app.schemas.user import MailVerifyOTP, UserCreate, UserResponse
from app.services import user_service


router = APIRouter(tags=["Auth"])


@router.post("/signin", response_model=CommonResponse)
async def create_user(
    user: UserCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):

    if user_service.email_exists(db, user.email):
        return error_response("Email already exist", 404)

    created = user_service.create_user(db, user)
    if not created:
        return error_response("User not created", 404)
    else:
        otp = generateOtp()
        await redisCache.set(created.email, otp, settings.OTP_EXPIRY)
        message = MailSchema(
            recipient=created.email,
            subject="Register Successful - FastAPI",
            body=f"<p>Hi <strong>{created.name}</strong>,</p><p style='color:blue; background: yellow;'>Welcome to fastAPI. Your OTP is <code>{otp}</code>.</p>",
        )

        background_tasks.add_task(mailSend, message)

        return success_response(
            data=jsonable_encoder(UserResponse.model_validate(created)),
            message="User created",
        )


@router.post("/login", response_model=CommonResponse)
async def login(req: LoginSchema, db: Session = Depends(get_db)):
    user = user_service.get_user_by_mail(db, req.email)
    if not user:
        return error_response("Email & password incorrect")

    if verifyPassword(req.password, user.password):
        token = createAccessToken(user.id)
        user = jsonable_encoder(UserResponse.model_validate(user))
        return success_response(
            data={"user": user, "token": token}, message="Login success"
        )
    else:
        return error_response("Email & password incorrect")


@router.post("/verify-otp", response_model=CommonResponse)
async def verifyOTP(req: MailVerifyOTP, db: Session = Depends(get_db)):
    otp = await redisCache.get(req.email)
    if req.otp == otp:
        updated = user_service.update_verified_user(db, req.email)

        if not updated:
            return error_response("Mail not verified", 400)
        else:
            await redisCache.delete(req.email)
            return success_response(message="Mail verified")

    else:
        return error_response("Mail not verified", 400)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


@router.get("/profile", response_model=CommonResponse)
def get_current_user(current_user: CurrentUser):
    return success_response(data=current_user)
