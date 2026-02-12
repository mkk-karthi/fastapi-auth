from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api import router
from app.core.logger import configure_logger
from app.core.response import (
    http_exception_handler,
    rate_limit_exceeded_handler,
    validation_exception_handler,
)

app = FastAPI(
    title="FastAPI Starter Project",
    description="FastAPI Starter Project",
    version="1.0",
    docs_url="/api/documentation/",
    openapi_url="/api/openapi.json",
)

configure_logger()

# Set all CORS enabled origins
origins = [
    "http://localhost:3000",  # Example origin for local development
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# initialize limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
app.state.limiter = limiter


# handle error response
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Set global rate limit
app.add_middleware(SlowAPIMiddleware)


@app.get("/")
@limiter.limit("2/minute")
async def read_root(request: Request):
    logger.info("Works done")
    return {"message": "Hello, FastAPI!"}

app.include_router(router.router)
