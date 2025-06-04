from typing import Optional, List, Dict, Any
from datetime import date
from pydantic import BaseModel

class PaginationParams(BaseModel):
    page: int = 1
    per_page: int = 10
    
class SortParams(BaseModel):
    field: str
    order: str = "asc"

class FilterParams(BaseModel):
    field: str
    operator: str
    value: Any

class QueryParams(BaseModel):
    pagination: Optional[PaginationParams] = None
    sort: Optional[List[SortParams]] = None
    filters: Optional[List[FilterParams]] = None
    search: Optional[str] = None

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    per_page: int
    pages: int

class ErrorResponse(BaseModel):
    detail: str
    code: Optional[str] = None

class SuccessResponse(BaseModel):
    message: str
    data: Optional[Dict[str, Any]] = None