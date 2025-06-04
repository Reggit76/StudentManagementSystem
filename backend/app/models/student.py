from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, date
from pydantic import Field, field_validator, BaseModel, EmailStr
from .base import BaseDBModel, BaseCreateModel, BaseUpdateModel
from .student_data import StudentData, StudentDataCreate, StudentDataUpdate
from .additional_status import AdditionalStatus

if TYPE_CHECKING:
    from .hostel_student import HostelStudent
    from .contribution import Contribution


class StudentBase(BaseModel):
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    email: EmailStr
    phone: str
    birth_date: date
    group_id: int
    is_active: bool = True
    dormitory_room: Optional[str] = None


class Student(BaseDBModel, StudentBase):
    """Модель студента из БД"""
    id: int
    data_id: Optional[int] = None
    student_data: Optional[StudentData] = None
    additional_statuses: List[AdditionalStatus] = []
    group_name: Optional[str] = None
    subdivision_name: Optional[str] = None


class StudentCreate(BaseCreateModel, StudentBase):
    """Модель для создания студента"""
    student_data: Optional[StudentDataCreate] = None
    additional_status_ids: List[int] = Field(default_factory=list)


class StudentUpdate(BaseUpdateModel):
    """Модель для обновления студента"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    birth_date: Optional[date] = None
    group_id: Optional[int] = None
    is_active: Optional[bool] = None
    dormitory_room: Optional[str] = None
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
    pass


class StudentWithDetails(Student):
    """Модель студента с полными деталями"""
    hostel_info: Optional['HostelStudent'] = None
    contributions: List['Contribution'] = []