from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from pydantic import Field, field_validator, BaseModel
from .base import BaseDBModel, BaseCreateModel, BaseUpdateModel
from .student_data import StudentData, StudentDataCreate, StudentDataUpdate
from .additional_status import AdditionalStatus

if TYPE_CHECKING:
    from .hostel_student import HostelStudent
    from .contribution import Contribution


class StudentBase(BaseModel):
    group_id: int = Field(..., description="ID группы")
    full_name: str = Field(..., description="ФИО студента")
    is_active: bool = Field(default=False, description="Активный член профсоюза")
    is_budget: bool = Field(..., description="Бюджетник")
    year: int = Field(..., ge=2000, le=2100, description="Год поступления")


class Student(BaseDBModel, StudentBase):
    """Модель студента из БД"""
    data_id: Optional[int] = Field(None, description="ID дополнительных данных")
    student_data: Optional[StudentData] = Field(None, description="Дополнительные данные")
    additional_statuses: List[AdditionalStatus] = Field(default_factory=list, description="Дополнительные статусы")
    group_name: Optional[str] = Field(None, description="Название группы")
    subdivision_name: Optional[str] = Field(None, description="Название подразделения")


class StudentCreate(BaseCreateModel, StudentBase):
    """Модель для создания студента"""
    student_data: Optional[StudentDataCreate] = None
    additional_status_ids: List[int] = Field(default_factory=list)


class StudentUpdate(BaseUpdateModel):
    """Модель для обновления студента"""
    group_id: Optional[int] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_budget: Optional[bool] = None
    year: Optional[int] = Field(None, ge=2000, le=2100)
    student_data: Optional[StudentDataUpdate] = None
    additional_status_ids: Optional[List[int]] = None

    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v):
        if v is None:
            return v
        if not v.strip():
            raise ValueError('ФИО не может быть пустым')
        parts = v.strip().split()
        if len(parts) < 2:
            raise ValueError('ФИО должно содержать минимум фамилию и имя')
        return ' '.join(parts)


class StudentInDB(Student):
    """Модель студента в БД"""
    pass


class StudentWithDetails(Student):
    """Модель студента с полными деталями"""
    hostel_info: Optional['HostelStudent'] = None
    contributions: List['Contribution'] = []


class BulkOperationResult(BaseModel):
    """Результат массовой операции"""
    success_count: int
    error_count: int
    errors: List[str] = Field(default_factory=list)