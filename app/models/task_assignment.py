from tokenize import Comment
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TaskAssignmentBase(BaseModel):
    task_id: int
    assignee_id: int
    assigner_id: int

class TaskAssignmentCreate(TaskAssignmentBase):
    pass
class TaskAssignment(BaseModel):
    task_id :int
    user_id:int
    comment:str
    deadline: datetime
class TaskAssignmentOut(BaseModel):
    assignment_id: int
    group_name: Optional[str] = None
    task_title: str
    comment: Optional[str] = None
    status : str
    deadline: Optional[datetime] = None
    group_id : int 
class AssignmentUpdate(BaseModel):
    status: Optional[str] = None
    deadline: Optional[datetime] = None
    comment: Optional[str] = None