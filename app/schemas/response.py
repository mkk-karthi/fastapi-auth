from typing import Any, Dict, Generic, List, TypeVar, Union
from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T")


class PaginationMeta(GenericModel, Generic[T]):
    items: List[T]
    page: int
    size: int
    total: int


class SuccessResponse(GenericModel, Generic[T]):
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
