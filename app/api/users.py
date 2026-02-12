from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services import user_service


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=UserResponse)
def get_users(db: Session = Depends(get_db)):
    return user_service.get_users(db)


@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return user_service.create_user(db, user)


@router.put("/{id}", response_model=UserResponse)
def update_user(id: int, user: UserUpdate, db: Session = Depends(get_db)):
    updated = user_service.update_user(db, id, user)
    if not updated:
        HTTPException(status_code=404, detail="User not found")
    return updated


@router.get("/{id}", response_model=UserResponse)
def get_user(id: int, db: Session = Depends(get_db)):
    updated = user_service.get_user(db, id)
    if not updated:
        HTTPException(status_code=404, detail="User not found")
    return updated


@router.delete("/{id}", response_model=UserResponse)
def delete_user(id: int, db: Session = Depends(get_db)):
    deleted = user_service.delete_user(db, id)
    if not deleted:
        HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}
