import re
from pydantic import BaseModel, EmailStr, Field, field_validator

password_pattern = r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[\W]).{8,16}$"


class LoginSchema(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def validatePassword(cls, v: str):
        if not re.match(password_pattern, v):
            raise ValueError(
                "Password must be 8-16 chars with uppercase, lowercase, number, and special character"
            )

        return v
