import asyncpg
from typing import List, Dict, Any, Union
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from datetime import datetime
from app.models import notification

from app.api.deps import get_current_user, get_db_conn
from app.api.crud.notifications_crud import delete_all_notifications_by_user, get_notifications_by_user

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("/",response_model=List[notification.NotificationOut])
async def get_noti(
    conn:asyncpg.Connection=Depends(get_db_conn), 
    current_user=Depends(get_current_user)):
    return await get_notifications_by_user(conn,current_user["user_id"])
@router.delete("/",status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_noti(
    conn:asyncpg.Connection=Depends(get_db_conn), 
    current_user=Depends(get_current_user)
):
    await delete_all_notifications_by_user(conn,current_user["user_id"])