import re
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from app.core.config import settings

password_pattern = r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[\W]).{8,16}$"


def validate_password_strength(v: str):
    if not re.match(password_pattern, v):
        raise ValueError(
            "Password must be 8-16 chars with uppercase, lowercase, number, and special character"
        )
    return v


class PasswordSchema(BaseModel):
    password: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def validatePassword(cls, v: str):
        return validate_password_strength(v)

    confirm_password: str = Field(..., min_length=8)

    @model_validator(mode="after")
    def check_passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class LoginSchema(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def validatePassword(cls, v: str):
        return validate_password_strength(v)


class SigninSchema(PasswordSchema):
    name: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class MailVerifyOTP(BaseModel):
    email: EmailStr
    otp: str = Field(
        ...,
        min_length=settings.OTP_LENGTH,
        max_length=settings.OTP_LENGTH,
        pattern=r"^\d+$",
    )


class ChangePasswordSchema(PasswordSchema):
    old_password: str = Field(..., min_length=8)

    @field_validator("old_password")
    @classmethod
    def validate_old_password(cls, v: str):
        return validate_password_strength(v)


class ResetPasswordSchema(PasswordSchema):
    email: EmailStr
    otp: str = Field(
        ...,
        min_length=settings.OTP_LENGTH,
        max_length=settings.OTP_LENGTH,
        pattern=r"^\d+$",
    )
