from typing import Optional, List, Dict, Any, Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar('T')


class QueryParams(BaseModel):
    """Параметры запроса с пагинацией и сортировкой"""
    page: int = Field(default=1, ge=1, description="Номер страницы")
    size: int = Field(default=50, ge=1, le=100, description="Размер страницы")
    sort_by: Optional[str] = Field(None, description="Поле для сортировки")
    sort_order: str = Field(default="asc", description="Порядок сортировки")


class PaginationParams(BaseModel):
    """Параметры пагинации"""
    page: int = Field(default=1, ge=1)
    size: int = Field(default=50, ge=1, le=100)


class SortParams(BaseModel):
    """Параметры сортировки"""
    field: str
    order: str = Field(default="asc", pattern="^(asc|desc)$")


class FilterParams(BaseModel):
    """Параметры фильтрации"""
    field: str
    operator: str
    value: Any


class PaginatedResponse(BaseModel, Generic[T]):
    """Пагинированный ответ"""
    items: List[T]
    total: int = Field(..., description="Общее количество записей")
    page: int = Field(..., description="Текущая страница")
    size: int = Field(..., description="Размер страницы")
    pages: int = Field(..., description="Общее количество страниц")


class ErrorResponse(BaseModel):
    """Ответ с ошибкой"""
    detail: str
    code: Optional[str] = None


class SuccessResponse(BaseModel):
    """Ответ об успешной операции"""
    message: str
    data: Optional[Dict[str, Any]] = None


class BulkOperationResult(BaseModel):
    """Результат массовой операции"""
    success_count: int = Field(..., description="Количество успешных операций")
    error_count: int = Field(..., description="Количество ошибок")
    errors: List[str] = Field(default_factory=list, description="Список ошибок")