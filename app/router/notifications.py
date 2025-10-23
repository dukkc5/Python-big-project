from anyio import current_effective_deadline
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import asyncpg
from datetime import datetime

from app.api.crud import task_crud
from app.api.crud.task_crud import create_group_tasks, create_users_tasks, get_group_id_by_task_id, get_group_tasks
from app.models.notification import NotificationCreate,NotificationOut
from app.router.auth import get_user_by_account
from app.config.db import get_db
from app.api.deps import get_current_user, get_db_conn,check_user_role
from app.api.crud.group_crud import get_group_id,get_user_role
from asyncpg.exceptions import ForeignKeyViolationError
from pydantic import BaseModel
from asyncpg import PostgresError, exceptions

router = APIRouter(prefix="/notifications",tags=["notifications"])
@router.post("/",status_code=200)
async def create_noti(
    notification:NotificationOut,
    current_user=Depends(get_current_user),
    conn: asyncpg.Connection=Depends(get_db_conn)
):
    try:

    