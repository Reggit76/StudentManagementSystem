from typing import Optional
from pydantic import BaseModel, Field
from .base import BaseDBModel, BaseCreateModel, BaseUpdateModel


class GroupBase(BaseModel):
    name: str = Field(..., description="Название группы")
    subdivision_id: int = Field(..., description="ID подразделения")
    year: int = Field(..., ge=2000, le=2100, description="Год группы")


class Group(BaseDBModel, GroupBase):
    """Модель группы из БД"""
    students_count: int = Field(default=0, description="Количество студентов")
    active_students_count: int = Field(default=0, description="Количество активных студентов")
    subdivision_name: Optional[str] = Field(None, description="Название подразделения")


class GroupCreate(BaseCreateModel, GroupBase):
    """Модель для создания группы"""
    pass


class GroupUpdate(BaseUpdateModel):
    """Модель для обновления группы"""
    name: Optional[str] = None
    subdivision_id: Optional[int] = None
    year: Optional[int] = Field(None, ge=2000, le=2100)


class GroupWithStats(Group):
    """Группа с расширенной статистикой"""
    budget_students_count: int = Field(default=0, description="Количество бюджетников")


class GroupInDB(Group):
    """Модель группы в БД"""
    pass