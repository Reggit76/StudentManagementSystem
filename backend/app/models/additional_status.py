from typing import Optional
from pydantic import BaseModel
from .base import BaseDBModel, BaseCreateModel, BaseUpdateModel


class AdditionalStatusBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True


class AdditionalStatus(BaseDBModel, AdditionalStatusBase):
    pass


class AdditionalStatusCreate(BaseCreateModel, AdditionalStatusBase):
    """Модель для создания дополнительного статуса"""
    pass


class AdditionalStatusUpdate(BaseUpdateModel):
    """Модель для обновления дополнительного статуса"""
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class AdditionalStatusInDB(AdditionalStatus):
    pass