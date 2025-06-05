from typing import Optional
from pydantic import BaseModel, Field
from .base import BaseDBModel, BaseCreateModel, BaseUpdateModel


class AdditionalStatusBase(BaseModel):
    name: str = Field(..., description="Название статуса")


class AdditionalStatus(BaseDBModel, AdditionalStatusBase):
    """Модель дополнительного статуса из БД"""
    pass


class AdditionalStatusCreate(BaseCreateModel, AdditionalStatusBase):
    """Модель для создания дополнительного статуса"""
    pass


class AdditionalStatusUpdate(BaseUpdateModel):
    """Модель для обновления дополнительного статуса"""
    name: Optional[str] = None