from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class TaskOut(BaseModel):
    task_id : int
    title: str
    description: Optional[str]
    status :str
    deadline : date


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

class TaskAssignmentRequest(BaseModel):
    task_id: int
    user_id_to_assign: int 
    comment: Optional[str] = None
