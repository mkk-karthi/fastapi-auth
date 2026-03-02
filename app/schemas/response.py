from typing import Dict, Generic, List, TypeVar, Union
from pydantic import BaseModel

T = TypeVar("T")


class PaginationMeta(BaseModel, Generic[T]):
    items: List[T]
    page: int
    size: int
    total: int


class SuccessResponse(BaseModel, Generic[T]):
    code: int = 200
    message: str = "Success"
    data: T = None


class ErrorResponse(BaseModel):
    code: int
    message: str


class ValidationErrorResponse(BaseModel):
    code: int = 422
    message: str = "Validation error"
    error: Dict


class HTTPExceptionResponse(BaseModel):
    code: int
    message: str


CommonResponse = Union[SuccessResponse, ValidationErrorResponse, ErrorResponse]
