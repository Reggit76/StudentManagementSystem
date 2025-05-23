from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from pydantic import Field, field_validator
from .base import BaseDBModel
from .student_data import StudentData, StudentDataCreate, StudentDataUpdate
from .additional_status import AdditionalStatus

if TYPE_CHECKING:
    from .hostel_student import HostelStudent
    from .contribution import Contribution


class StudentBase(BaseDBModel):
    """Базовая модель студента"""
    group_id: int = Field(..., gt=0, description="ID группы")
    full_name: str = Field(..., min_length=1, max_length=255, description="ФИО студента")
    is_active: bool = Field(False, description="Активный член профсоюза")
    is_budget: bool = Field(..., description="Бюджетник")
    year: int = Field(default_factory=lambda: datetime.now().year, ge=2000, le=2100)

    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v):
        if not v or not v.strip():
            raise ValueError('ФИО не может быть пустым')
        # Проверка на минимум два слова (фамилия и имя)
        parts = v.strip().split()
        if len(parts) < 2:
            raise ValueError('ФИО должно содержать минимум фамилию и имя')
        return ' '.join(parts)  # Нормализуем пробелы


class StudentCreate(StudentBase):
    """Модель для создания студента"""
    student_data: Optional[StudentDataCreate] = None
    additional_status_ids: List[int] = Field(default_factory=list)


class StudentUpdate(BaseDBModel):
    """Модель для обновления студента"""
    group_id: Optional[int] = Field(None, gt=0)
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
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


class Student(StudentBase):
    """Модель студента из БД"""
    id: int
    data_id: Optional[int] = None
    student_data: Optional[StudentData] = None
    additional_statuses: List[AdditionalStatus] = []
    group_name: Optional[str] = None
    subdivision_name: Optional[str] = None


class StudentWithDetails(Student):
    """Модель студента с полными деталями"""
    hostel_info: Optional['HostelStudent'] = None
    contributions: List['Contribution'] = []