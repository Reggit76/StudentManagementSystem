from typing import Optional
from datetime import date
from pydantic import BaseModel, Field
from .base import BaseDBModel, BaseCreateModel, BaseUpdateModel


class StudentDataBase(BaseModel):
    phone: Optional[str] = Field(None, description="Номер телефона")
    email: Optional[str] = Field(None, description="Email адрес")
    birthday: Optional[date] = Field(None, description="Дата рождения")


class StudentData(BaseDBModel, StudentDataBase):
    """Модель дополнительных данных студента из БД"""
    pass


class StudentDataCreate(BaseCreateModel, StudentDataBase):
    """Модель для создания данных студента"""
    pass


class StudentDataUpdate(BaseUpdateModel):
    """Модель для обновления данных студента"""
    phone: Optional[str] = None
    email: Optional[str] = None
    birthday: Optional[date] = None