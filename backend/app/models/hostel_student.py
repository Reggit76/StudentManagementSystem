from typing import Optional
from pydantic import BaseModel, Field
from .base import BaseDBModel, BaseCreateModel, BaseUpdateModel


class HostelStudentBase(BaseModel):
    student_id: int = Field(..., description="ID студента")
    hostel: int = Field(..., ge=1, le=20, description="Номер общежития")
    room: int = Field(..., ge=1, description="Номер комнаты")
    comment: Optional[str] = Field(None, description="Комментарий")


class HostelStudent(BaseDBModel, HostelStudentBase):
    """Модель проживающего в общежитии из БД"""
    student_name: Optional[str] = Field(None, description="ФИО студента")


class HostelStudentCreate(BaseCreateModel, HostelStudentBase):
    """Модель для создания записи о проживании"""
    pass


class HostelStudentUpdate(BaseUpdateModel):
    """Модель для обновления записи о проживании"""
    hostel: Optional[int] = Field(None, ge=1, le=20)
    room: Optional[int] = Field(None, ge=1)
    comment: Optional[str] = None