
from anyio import current_effective_deadline
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import asyncpg
from datetime import datetime

from app.api.crud import task_crud
from app.api.crud.task_crud import create_group_tasks, create_users_tasks, get_group_id_by_task_id, get_group_tasks
from app.models.task import TaskAssignmentRequest, TaskOut, TaskCreate, TaskUpdate
from app.router.auth import get_user_by_email
from app.config.db import get_db
from app.api.deps import get_current_user, get_db_conn,check_user_role
from app.api.crud.group_crud import get_group_id,get_user_role
from asyncpg.exceptions import ForeignKeyViolationError
from pydantic import BaseModel

router = APIRouter(prefix="/tasks",tags=["tasks"])


@router.get("/",response_model=List[TaskOut])
async def read_group_tasks(
    group_id : int,
    current_user = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db_conn)
    
):
    if not await get_group_id(conn,group_id):
        raise HTTPException(404,"This group not found")
    await check_user_role(conn,group_id,current_user["user_id"])
    return await get_group_tasks(conn,group_id)

@router.post("/",status_code=200)
async def create_group_task(
    task :TaskCreate,
    current_user = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db_conn)
):
    creator_user_id = current_user["user_id"]
    if not await get_group_id(conn,task.group_id):
        raise HTTPException(404,"This group not found")
    role = await get_user_role(conn,task.group_id,creator_user_id)
    if role == 'member':
        raise HTTPException(403,"Not authorized")
    await create_group_tasks(conn,task)
    return {"msg":"Tao task thanh cong"}
@router.post("/assign", status_code=status.HTTP_201_CREATED)
async def assign_task(
    task_id :int,
    user_id :int,
    current_user=Depends(get_current_user),
    conn = Depends(get_db_conn)
):
    group_id= await get_group_id_by_task_id(conn,task_id)
    if not group_id:
        raise HTTPException(404,"ko tồn tại nhiệm vụ này")
    check_role = await get_user_role(conn,group_id,user_id)
    if not check_role:
        raise HTTPException(404,"ko có user này trong nhóm")
    role = await get_user_role(conn,group_id,current_user["user_id"])
    if role =="member":
        raise HTTPException(403, "ko có quyền")
    await create_users_tasks(conn,task_id,user_id,"do this task")
    return {"msg":"done"}

@router.delete("/{task_id}",status_code=status.HTTP_200_OK )
async def delete_task(
    group_id : int,
    task_id : int,
    current_user = Depends(get_current_user),
    conn:asyncpg.Connection = Depends(get_db_conn)
):
    if not await get_group_id(conn,group_id):
        raise HTTPException(404,"this group does not exist")
    role = await get_user_role(conn,group_id,current_user["user_id"])
    if not role:
        raise HTTPException(status_code=403, detail="You are not in this group")
    if role != "leader":
        raise HTTPException(status_code=403, detail="Not authorized")
    await task_crud.remove_task_id(conn, task_id)
    return {"message": "Deleted successfully"}

@router.put("/{task_id}", response_model=TaskOut)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    conn: asyncpg.Connection = Depends(get_db_conn),
    current_user=Depends(get_current_user),
):
    updated = await task_crud.update_task(conn, task_id, task_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return dict(updated)



