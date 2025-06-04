from enum import Enum
from pydantic import BaseModel
from .base import BaseDBModel, BaseCreateModel, BaseUpdateModel

class RoleType(str, Enum):
    CHAIRMAN = "CHAIRMAN"
    DEPUTY_CHAIRMAN = "DEPUTY_CHAIRMAN"
    DIVISION_HEAD = "DIVISION_HEAD"
    DORMITORY_HEAD = "DORMITORY_HEAD"

class RoleBase(BaseModel):
    name: str
    type: RoleType
    description: str | None = None

class Role(BaseDBModel, RoleBase):
    pass

class RoleCreate(BaseCreateModel, RoleBase):
    pass

class RoleUpdate(BaseUpdateModel):
    name: str | None = None
    type: RoleType | None = None
    description: str | None = None
