from typing import Any
from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded


def success_response(
    data: Any = None,
    message: str = "Success",
    code: int = 200,
):
    return JSONResponse(
        status_code=code,
        content={
            "code": code,
            "message": message,
            "data": data,
        },
    )


def error_response(
    message: str = "Error",
    code: int = 400,
):
    return JSONResponse(
        status_code=code,
        content={
            "code": code,
            "message": message,
        },
    )


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": "Rate limit exceeded",
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail,
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = {}
    for error in exc.errors():
        errors[error["loc"][-1]] = error["msg"]
    return JSONResponse(
        status_code=422,
        content={
            "code": 422,
            "message": "Validation error",
            "error": errors
        },
    )
