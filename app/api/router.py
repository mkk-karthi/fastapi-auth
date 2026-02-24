from fastapi import APIRouter

from app.api import auth, users


router = APIRouter(prefix="/api")
router.include_router(users.router)
router.include_router(auth.router)
