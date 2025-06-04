from typing import Optional
from pydantic import BaseModel
from .base import BaseDBModel, BaseCreateModel, BaseUpdateModel


class SubdivisionBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True


class Subdivision(BaseDBModel, SubdivisionBase):
    students_count: int = 0
    active_students_count: int = 0
    groups_count: int = 0


class SubdivisionCreate(BaseCreateModel, SubdivisionBase):
    pass


class SubdivisionUpdate(BaseUpdateModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class SubdivisionInDB(Subdivision):
    pass