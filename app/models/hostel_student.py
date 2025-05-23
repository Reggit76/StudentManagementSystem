from typing import Optional
from pydantic import Field, field_validator
from .base import BaseDBModel


class HostelStudentBase(BaseDBModel):
    """Базовая модель проживающего в общежитии"""
    student_id: int = Field(..., gt=0, description="ID студента")
    hostel: int = Field(..., gt=0, description="Номер общежития")
    room: int = Field(..., gt=0, description="Номер комнаты")
    comment: Optional[str] = Field(None, max_length=255, description="Комментарий")

    @field_validator('hostel')
    @classmethod
    def validate_hostel(cls, v):
        if v < 1 or v > 20:  # Предполагаем, что общежитий не больше 20
            raise ValueError('Номер общежития должен быть от 1 до 20')
        return v

    @field_validator('room')
    @classmethod
    def validate_room(cls, v):
        if v < 1 or v > 9999:  # Предполагаем 4-значные номера комнат максимум
            raise ValueError('Номер комнаты должен быть от 1 до 9999')
        return v


class HostelStudentCreate(HostelStudentBase):
    """Модель для создания записи о проживании в общежитии"""
    pass


class HostelStudentUpdate(BaseDBModel):
    """Модель для обновления записи о проживании в общежитии"""
    hostel: Optional[int] = Field(None, gt=0)
    room: Optional[int] = Field(None, gt=0)
    comment: Optional[str] = Field(None, max_length=255)

    @field_validator('hostel')
    @classmethod
    def validate_hostel(cls, v):
        if v is not None and (v < 1 or v > 20):
            raise ValueError('Номер общежития должен быть от 1 до 20')
        return v

    @field_validator('room')
    @classmethod
    def validate_room(cls, v):
        if v is not None and (v < 1 or v > 9999):
            raise ValueError('Номер комнаты должен быть от 1 до 9999')
        return v


class HostelStudent(HostelStudentBase):
    """Модель проживающего в общежитии из БД"""
    id: int
    student_name: Optional[str] = None