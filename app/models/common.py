from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field
from enum import Enum


T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """Модель для пагинированных ответов"""
    items: List[T]
    total: int
    page: int
    size: int
    pages: int

    class Config:
        from_attributes = True


class SortOrder(str, Enum):
    """Порядок сортировки"""
    ASC = "asc"
    DESC = "desc"


class QueryParams(BaseModel):
    """Базовые параметры запроса"""
    page: int = Field(1, ge=1, description="Номер страницы")
    size: int = Field(50, ge=1, le=100, description="Размер страницы")
    sort_by: Optional[str] = Field(None, description="Поле для сортировки")
    sort_order: SortOrder = Field(SortOrder.ASC, description="Порядок сортировки")


class ErrorResponse(BaseModel):
    """Модель ошибки"""
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None


class SuccessResponse(BaseModel):
    """Модель успешного ответа"""
    message: str
    data: Optional[dict] = None


class BulkOperationResult(BaseModel):
    """Результат массовой операции"""
    success_count: int = 0
    error_count: int = 0
    errors: List[dict] = []


class DateRangeFilter(BaseModel):
    """Фильтр по диапазону дат"""
    date_from: Optional[str] = None
    date_to: Optional[str] = None


class CSRFToken(BaseModel):
    """CSRF токен"""
    csrf_token: str