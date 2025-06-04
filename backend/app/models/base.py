from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class BaseDBModel(BaseModel):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True
    )

class BaseCreateModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

class BaseUpdateModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )