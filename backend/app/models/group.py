from typing import Optional
from pydantic import BaseModel
from .base import BaseDBModel, BaseCreateModel, BaseUpdateModel


class GroupBase(BaseModel):
    name: str
    division_id: int
    course: int
    is_active: bool = True


class Group(BaseDBModel, GroupBase):
    students_count: int = 0
    active_students_count: int = 0
    division_name: Optional[str] = None


class GroupCreate(BaseCreateModel, GroupBase):
    pass


class GroupUpdate(BaseUpdateModel):
    name: Optional[str] = None
    division_id: Optional[int] = None
    course: Optional[int] = None
    is_active: Optional[bool] = None


class GroupInDB(Group):
    pass