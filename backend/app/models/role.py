from typing import Optional
from pydantic import BaseModel, Field
from .base import BaseDBModel, BaseCreateModel, BaseUpdateModel


class RoleBase(BaseModel):
    name: str = Field(..., description="Название роли")


class Role(BaseDBModel, RoleBase):
    """Модель роли из БД"""
    pass


class RoleCreate(BaseCreateModel, RoleBase):
    """Модель для создания роли"""
    pass


class RoleUpdate(BaseUpdateModel):
    """Модель для обновления роли"""
    name: Optional[str] = None

class RoleType(BaseModel):
    name: Optional[str] = None
