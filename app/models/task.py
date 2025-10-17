from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TaskOut(BaseModel):
    title: str
    description: Optional[str]


class TaskCreate(BaseModel):
    title: str
    description: Optional[str]
    group_id: int
    deadline: Optional[datetime]


class TaskUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    status: Optional[str]
    deadline: Optional[datetime]
