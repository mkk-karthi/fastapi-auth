import re
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

password_pattern = r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[\W]).{8,16}$"


def validate_password_strength(v: str):
    if not re.match(password_pattern, v):
        raise ValueError(
            "Password must be 8-16 chars with uppercase, lowercase, number, and special character"
        )
    return v


class UserCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

    password: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str):
        return validate_password_strength(v)

    confirm_password: str = Field(..., min_length=8)

    @model_validator(mode="after")
    def check_passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class UserUpdate(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    password: str = Field(None, min_length=8)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str):
        return validate_password_strength(v)


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    avatar: str | None

    class Config:
        from_attributes = True  # SQLAlchemy → Pydantic
