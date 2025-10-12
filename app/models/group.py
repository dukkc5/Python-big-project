from pydantic import BaseModel
from typing import Optional

class GroupCreate(BaseModel):
    group_name: str
    description: Optional[str] = None

class GroupOut(BaseModel):
    group_id: int
    group_name: str
    description: Optional[str] = None