from typing import Annotated, Generator
from urllib.parse import quote_plus
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from app.core.config import settings

password = quote_plus(settings.DB_PASSWORD)
DATABASE_URL = (
    f"mysql+pymysql://{settings.DB_USERNAME}:"
    f"{password}@{settings.DB_HOST}:"
    f"{settings.DB_PORT}/{settings.DB_DATABASE}"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()


# Dependency
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

GetDB = Annotated[Session, Depends(get_db)]