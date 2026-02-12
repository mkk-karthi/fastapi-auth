from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded

from app.api import router
from app.core.database import Base, engine
from app.core.logger import configure_logger

app = FastAPI(
    title="FastAPI Starter Project",
    description="FastAPI Starter Project",
    version="1.0",
    docs_url="/api/docs/",
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


# Custom handler
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"error": "Rate limit exceeded"},
    )


app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)


@app.get("/")
@limiter.limit("2/minute")
async def read_root(request: Request):
    logger.info("Works done")
    return {"message": "Hello, FastAPI!"}


Base.metadata.create_all(bind=engine)

app.include_router(router.router)
