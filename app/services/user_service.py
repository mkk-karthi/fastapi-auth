from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def create_user(db: Session, user: UserCreate):
    new_user = User(name=user.name, email=user.email, password=user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def get_users(db: Session):
    db.query(User).all()


def get_user(db: Session, id: int):
    db.query(User).filter(User.id == id).first()


def update_user(db: Session, id: int, user: UserUpdate):
    db_user = get_user(db, id)
    if not db_user:
        return None

    db_user.name = user.name
    db_user.email = user.email
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, id: int):
    db_user = get_user(db, id)
    if not db_user:
        return None

    db.delete(db_user)
    db.commit()
    return db_user
