# backend/app/models/hostel_student.py

from typing import Optional
from pydantic import BaseModel, Field
from .base import BaseDBModel, BaseCreateModel, BaseUpdateModel


class HostelStudentBase(BaseModel):
    """Базовая модель проживающего в общежитии"""
    studentid: int = Field(..., description="ID студента", alias="student_id")
    hostel: int = Field(..., ge=1, le=20, description="Номер общежития")
    room: int = Field(..., ge=1, description="Номер комнаты")
    comment: Optional[str] = Field(None, description="Комментарий")

    model_config = {
        "populate_by_name": True,
        "from_attributes": True
    }


class HostelStudent(BaseDBModel, HostelStudentBase):
    """Модель проживающего в общежитии из БД"""
    student_name: Optional[str] = Field(None, description="ФИО студента")


class HostelStudentCreate(BaseCreateModel, HostelStudentBase):
    """Модель для создания записи о проживании"""
    pass


class HostelStudentUpdate(BaseUpdateModel):
    """Модель для обновления записи о проживании"""
    hostel: Optional[int] = Field(None, ge=1, le=20, description="Номер общежития")
    room: Optional[int] = Field(None, ge=1, description="Номер комнаты")
    comment: Optional[str] = Field(None, description="Комментарий")