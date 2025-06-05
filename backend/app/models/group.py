# backend/app/models/group.py

from typing import Optional
from pydantic import BaseModel, Field
from .base import BaseDBModel, BaseCreateModel, BaseUpdateModel


class GroupBase(BaseModel):
    """Базовая модель группы"""
    name: str = Field(..., description="Название группы")
    subdivisionid: int = Field(..., description="ID подразделения", alias="subdivision_id")
    year: int = Field(..., ge=2000, le=2100, description="Год группы")

    model_config = {
        "populate_by_name": True,
        "from_attributes": True
    }


class Group(BaseDBModel, GroupBase):
    """Модель группы из БД"""
    subdivision_name: Optional[str] = Field(None, description="Название подразделения")
    students_count: int = Field(default=0, description="Количество студентов")
    active_students_count: int = Field(default=0, description="Количество активных студентов")
    union_percentage: float = Field(default=0.0, description="Процент в профсоюзе")


class GroupCreate(BaseCreateModel, GroupBase):
    """Модель для создания группы"""
    pass


class GroupUpdate(BaseUpdateModel):
    """Модель для обновления группы"""
    name: Optional[str] = Field(None, description="Название группы")
    subdivisionid: Optional[int] = Field(None, description="ID подразделения", alias="subdivision_id")
    year: Optional[int] = Field(None, ge=2000, le=2100, description="Год группы")


class GroupWithStats(Group):
    """Группа с расширенной статистикой"""
    budget_students_count: int = Field(default=0, description="Количество бюджетников")


class GroupInDB(Group):
    """Модель группы в БД (legacy)"""
    pass