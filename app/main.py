from contextlib import asynccontextmanager
import time
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from app.api import router
from app.core.config import settings
from app.core.database import Base, Engine
from app.core.logger import configure_logger
from app.core.redis import RedisCache
from app.core.response import (
    http_exception_handler,
    rate_limit_exceeded_handler,
    validation_exception_handler,
)

redis_cache = RedisCache()


# redis connection
@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    await redis_cache.connect()
    app.state.redis = redis_cache
    logger.info("Redis connected")

    yield

    # SHUTDOWN
    await redis_cache.close()


app = FastAPI(
    title="FastAPI Starter Project",
    description="FastAPI Starter Project",
    version="1.0",
    docs_url="/api/docs/",
    redoc_url="/api/redoc/",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
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
limiter = Limiter(key_func=get_remote_address, default_limits=[settings.MAX_RATELIMIT])
app.state.limiter = limiter


# handle error response
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, http_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Set global rate limit
app.add_middleware(SlowAPIMiddleware)


# Add Log for request and response
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Process the request
        response = await call_next(request)

        # Calculate the duration
        process_time = time.time() - start_time

        # Log summary details for immediate visibility
        logger.info(
            f"Request: {request.method} {request.url.path} from {request.client.host} | "
            f"Status: {response.status_code} | Duration: {process_time:.4f}s"
        )

        return response


app.add_middleware(LoggingMiddleware)
Base.metadata.create_all(bind=Engine)


@app.get("/")
async def read_root(request: Request):
    return {"message": "Hello, FastAPI!"}


app.include_router(router.router)
