from typing import Optional
from pydantic import Field, field_validator
from .base import BaseDBModel


class SubdivisionBase(BaseDBModel):
    """Базовая модель подразделения"""
    name: str = Field(..., min_length=1, max_length=16, description="Название подразделения")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Название подразделения не может быть пустым')
        return v.strip()


class SubdivisionCreate(SubdivisionBase):
    """Модель для создания подразделения"""
    pass


class SubdivisionUpdate(BaseDBModel):
    """Модель для обновления подразделения"""
    name: Optional[str] = Field(None, min_length=1, max_length=16)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Название подразделения не может быть пустым')
        return v.strip() if v else v


class Subdivision(SubdivisionBase):
    """Модель подразделения из БД"""
    id: int


class SubdivisionWithStats(Subdivision):
    """Модель подразделения с статистикой"""
    groups_count: int = 0
    students_count: int = 0
    users_count: int = 0