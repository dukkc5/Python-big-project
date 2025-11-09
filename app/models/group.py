from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class GroupCreate(BaseModel):
    group_name: str
    description: Optional[str] = None

class GroupOut(BaseModel): # ten bien nay phai giong ten bien trong db
    group_id: int 
    group_name: str
    description: Optional[str] = None
class MemberAdd(BaseModel):
    account:str
class MemberToLeader(BaseModel):
    account:str
class GroupOutWithDetails(BaseModel):
    group_id: int 
    group_name: str
    description: Optional[str] = None
    my_role: str
    last_message_sender: Optional[str] = None
    last_message_content : Optional[str] = None
    last_message_timestamp : Optional[datetime] = None
    avatarUrl: Optional[str] = None
class GroupUpdate(BaseModel):
    group_name: Optional[str] = None
    description: Optional[str] = None


    
