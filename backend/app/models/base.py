# backend/app/models/base.py

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class BaseDBModel(BaseModel):
    """Базовая модель для объектов из БД"""
    id: int = Field(..., description="Уникальный идентификатор")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: Optional[datetime] = Field(None, description="Дата последнего обновления")

    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        validate_assignment=True
    )


class BaseCreateModel(BaseModel):
    """Базовая модель для создания объектов"""
    
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        validate_assignment=True
    )


class BaseUpdateModel(BaseModel):
    """Базовая модель для обновления объектов"""
    
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        validate_assignment=True,
        exclude_unset=True
    )