from pydantic import Field
from .base import BaseDBModel


class StudentAdditionalStatusBase(BaseDBModel):
    """Базовая модель связи студент-дополнительный статус"""
    student_id: int = Field(..., gt=0, description="ID студента")
    status_id: int = Field(..., gt=0, description="ID статуса")


class StudentAdditionalStatusCreate(StudentAdditionalStatusBase):
    """Модель для создания связи студент-дополнительный статус"""
    pass


class StudentAdditionalStatus(StudentAdditionalStatusBase):
    """Модель связи студент-дополнительный статус из БД"""
    pass