from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import asyncpg
from datetime import datetime

from app.api.crud.task_crud import get_group_tasks
from app.models.task import TaskOut, TaskCreate, TaskUpdate
from app.router.auth import get_user_by_email
from app.config.db import get_db
from app.api.deps import get_current_user, get_db_conn,check_user_role
from app.api.crud.group_crud import get_group_id,get_user_role

router = APIRouter(prefix="/tasks",tags=["tasks"])
@router.get("/",response_model=List[TaskOut])
async def read_user_tasks(
    group_id : int,
    current_user = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db_conn)
    
):
    if not await get_group_id(conn,group_id):
        raise HTTPException(404,"This group not found")
    await check_user_role(conn,group_id,current_user["user_id"])
    return await get_group_tasks(conn,group_id)
