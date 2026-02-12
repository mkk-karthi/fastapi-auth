from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    name: str = Field(...,min_length=3,max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(...,min_length=8)


class UserUpdate(UserBase):
    password: str = Field(...,min_length=8)


class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True  # SQLAlchemy → Pydantic
