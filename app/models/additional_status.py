from typing import Optional
from pydantic import Field, field_validator
from .base import BaseDBModel


class AdditionalStatusBase(BaseDBModel):
    """Базовая модель дополнительного статуса"""
    name: str = Field(..., min_length=1, max_length=50, description="Название статуса")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Название статуса не может быть пустым')
        return v.strip()


class AdditionalStatusCreate(AdditionalStatusBase):
    """Модель для создания дополнительного статуса"""
    pass


class AdditionalStatusUpdate(BaseDBModel):
    """Модель для обновления дополнительного статуса"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Название статуса не может быть пустым')
        return v.strip() if v else v


class AdditionalStatus(AdditionalStatusBase):
    """Модель дополнительного статуса из БД"""
    id: int