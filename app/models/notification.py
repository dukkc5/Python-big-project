from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class NotificationCreate(BaseModel):
    user_id: int
    message: str
    type: Optional[str] = None
    task_id: Optional[int] = None

class NotificationOut(BaseModel):
    notification_id: int
    user_id: int
    message: str
    created_at: datetime    
