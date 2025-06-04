from typing import Optional
from datetime import date
from pydantic import BaseModel
from .base import BaseDBModel, BaseCreateModel, BaseUpdateModel


class StudentAdditionalStatusBase(BaseModel):
    student_id: int
    status_id: int
    start_date: date
    end_date: Optional[date] = None
    is_active: bool = True


class StudentAdditionalStatus(BaseDBModel, StudentAdditionalStatusBase):
    status_name: Optional[str] = None


class StudentAdditionalStatusCreate(BaseCreateModel, StudentAdditionalStatusBase):
    pass


class StudentAdditionalStatusUpdate(BaseUpdateModel):
    status_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: Optional[bool] = None