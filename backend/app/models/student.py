# backend/app/models/student.py

from typing import Optional, List, TYPE_CHECKING
from pydantic import Field, field_validator, BaseModel
from .base import BaseDBModel, BaseCreateModel, BaseUpdateModel

if TYPE_CHECKING:
    from .student_data import StudentData, StudentDataCreate, StudentDataUpdate
    from .additional_status import AdditionalStatus
    from .hostel_student import HostelStudent
    from .contribution import Contribution


class StudentBase(BaseModel):
    """Базовая модель студента"""
    groupid: int = Field(..., description="ID группы", alias="group_id")
    fullname: str = Field(..., description="ФИО студента", alias="full_name")
    isactive: bool = Field(default=False, description="Активный член профсоюза", alias="is_active")
    isbudget: bool = Field(..., description="Бюджетник", alias="is_budget")
    year: int = Field(..., ge=2000, le=2100, description="Год поступления")

    model_config = {
        "populate_by_name": True,
        "from_attributes": True
    }


class Student(BaseDBModel, StudentBase):
    """Модель студента из БД"""
    dataid: Optional[int] = Field(None, description="ID дополнительных данных", alias="data_id")
    
    # Дополнительные поля для JOIN-ов
    group_name: Optional[str] = Field(None, description="Название группы")
    subdivision_name: Optional[str] = Field(None, description="Название подразделения")
    
    # Связанные объекты (заполняются отдельно)
    student_data: Optional['StudentData'] = Field(None, description="Дополнительные данные")
    additional_statuses: List['AdditionalStatus'] = Field(default_factory=list, description="Дополнительные статусы")
    
    @field_validator('fullname')
    @classmethod
    def validate_full_name(cls, v):
        if not v or not v.strip():
            raise ValueError('ФИО не может быть пустым')
        parts = v.strip().split()
        if len(parts) < 2:
            raise ValueError('ФИО должно содержать минимум фамилию и имя')
        return ' '.join(parts)


class StudentCreate(BaseCreateModel, StudentBase):
    """Модель для создания студента"""
    student_data: Optional['StudentDataCreate'] = Field(None, description="Дополнительные данные студента")
    additional_status_ids: List[int] = Field(default_factory=list, description="ID дополнительных статусов")


class StudentUpdate(BaseUpdateModel):
    """Модель для обновления студента"""
    groupid: Optional[int] = Field(None, description="ID группы", alias="group_id")
    fullname: Optional[str] = Field(None, description="ФИО студента", alias="full_name")
    isactive: Optional[bool] = Field(None, description="Активный член профсоюза", alias="is_active")
    isbudget: Optional[bool] = Field(None, description="Бюджетник", alias="is_budget")
    year: Optional[int] = Field(None, ge=2000, le=2100, description="Год поступления")
    student_data: Optional['StudentDataUpdate'] = Field(None, description="Дополнительные данные")
    additional_status_ids: Optional[List[int]] = Field(None, description="ID дополнительных статусов")

    @field_validator('fullname')
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


class StudentWithDetails(Student):
    """Модель студента с полными деталями"""
    hostel_info: Optional['HostelStudent'] = Field(None, description="Информация об общежитии")
    contributions: List['Contribution'] = Field(default_factory=list, description="Взносы студента")


class BulkOperationResult(BaseModel):
    """Результат массовой операции"""
    success_count: int = Field(..., description="Количество успешных операций")
    error_count: int = Field(..., description="Количество ошибок")
    errors: List[str] = Field(default_factory=list, description="Список ошибок")


class StudentInDB(Student):
    """Модель студента в БД (legacy)"""
    pass