from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TaskAssignmentBase(BaseModel):
    task_id: int
    assignee_id: int
    assigner_id: int

class TaskAssignmentCreate(TaskAssignmentBase):
    pass

class TaskAssignmentOut(BaseModel):
    task_id: int
    task_name: str
    group_name: str
    assigned_by: str
    status: Optional[str]
    deadline: Optional[datetime]

class AssignmentUpdate(BaseModel):
    status: Optional[str] = None
    deadline: Optional[str] = None
    comment: Optional[str] = None