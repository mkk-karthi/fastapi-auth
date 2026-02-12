from fastapi import APIRouter

from app.api import users


router = APIRouter(prefix="/api")
router.include_router(users.router)
