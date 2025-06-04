from typing import Optional
from datetime import date
from pydantic import BaseModel
from .base import BaseDBModel, BaseCreateModel, BaseUpdateModel


class HostelStudentBase(BaseModel):
    student_id: int
    room_number: str
    check_in_date: date
    check_out_date: Optional[date] = None
    is_active: bool = True
    notes: Optional[str] = None


class HostelStudent(BaseDBModel, HostelStudentBase):
    student_name: Optional[str] = None
    group_name: Optional[str] = None


class HostelStudentCreate(BaseCreateModel, HostelStudentBase):
    pass


class HostelStudentUpdate(BaseUpdateModel):
    room_number: Optional[str] = None
    check_in_date: Optional[date] = None
    check_out_date: Optional[date] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None