from pydantic import BaseModel, EmailStr
from typing import Optional

class GroupCreate(BaseModel):
    group_name: str
    description: Optional[str] = None

class GroupOut(BaseModel): # ten bien nay phai giong ten bien trong db
    group_id: int 
    group_name: str
    description: Optional[str] = None
class MemberAdd(BaseModel):
    email: EmailStr
class MemberToLeader(BaseModel):
    email: EmailStr
    
