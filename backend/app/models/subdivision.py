from typing import Optional
from pydantic import BaseModel, Field
from .base import BaseDBModel, BaseCreateModel, BaseUpdateModel


class SubdivisionBase(BaseModel):
    name: str = Field(..., description="Название подразделения")


class Subdivision(BaseDBModel, SubdivisionBase):
    """Модель подразделения из БД"""
    students_count: int = Field(default=0, description="Количество студентов")
    active_students_count: int = Field(default=0, description="Количество активных студентов")
    groups_count: int = Field(default=0, description="Количество групп")
    union_percentage: float = Field(default=0.0, description="Процент в профсоюзе")


class SubdivisionCreate(BaseCreateModel, SubdivisionBase):
    """Модель для создания подразделения"""
    pass


class SubdivisionUpdate(BaseUpdateModel):
    """Модель для обновления подразделения"""
    name: Optional[str] = None


class SubdivisionWithStats(Subdivision):
    """Подразделение с расширенной статистикой"""
    users_count: int = Field(default=0, description="Количество пользователей")


class SubdivisionInDB(Subdivision):
    """Модель подразделения в БД"""
    pass