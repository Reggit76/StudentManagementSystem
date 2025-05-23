from typing import Optional
from pydantic import Field, field_validator
from .base import BaseDBModel


class RoleBase(BaseDBModel):
    """Базовая модель роли"""
    name: str = Field(..., min_length=1, max_length=50, description="Название роли")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Название роли не может быть пустым')
        return v.strip()


class RoleCreate(RoleBase):
    """Модель для создания роли"""
    pass


class RoleUpdate(BaseDBModel):
    """Модель для обновления роли"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Название роли не может быть пустым')
        return v.strip() if v else v


class Role(RoleBase):
    """Модель роли из БД"""
    id: int
