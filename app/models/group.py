from typing import Optional
from pydantic import Field, field_validator
from datetime import datetime
from .base import BaseDBModel


class GroupBase(BaseDBModel):
    """Базовая модель группы"""
    subdivision_id: int = Field(..., gt=0, description="ID подразделения")
    name: str = Field(..., min_length=1, max_length=255, description="Название группы")
    year: int = Field(default_factory=lambda: datetime.now().year, ge=2000, le=2100)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Название группы не может быть пустым')
        return v.strip()


class GroupCreate(GroupBase):
    """Модель для создания группы"""
    pass


class GroupUpdate(BaseDBModel):
    """Модель для обновления группы"""
    subdivision_id: Optional[int] = Field(None, gt=0)
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    year: Optional[int] = Field(None, ge=2000, le=2100)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Название группы не может быть пустым')
        return v.strip() if v else v


class Group(GroupBase):
    """Модель группы из БД"""
    id: int


class GroupWithStats(Group):
    """Модель группы со статистикой"""
    students_count: int = 0
    active_students_count: int = 0
    budget_students_count: int = 0
    subdivision_name: Optional[str] = None