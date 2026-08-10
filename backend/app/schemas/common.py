from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T | None = None
    error: dict | None = None


class PageMeta(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int


class Paginated(BaseModel, Generic[T]):
    items: list[T]
    meta: PageMeta


class ErrorOut(BaseModel):
    success: bool = False
    error: dict
