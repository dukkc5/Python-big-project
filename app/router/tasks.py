import logging
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import asyncpg
from datetime import datetime

from app.api.crud import task_crud
from app.api.crud.task_crud import create_group_tasks, get_group_tasks
from app.models.task import TaskAssignmentRequest, TaskOut, TaskCreate, TaskUpdate
from app.router.auth import get_user_by_email
from app.config.db import get_db
from app.api.deps import get_current_user, get_db_conn,check_user_role
from app.api.crud.group_crud import get_group_id,get_user_role
from asyncpg.exceptions import ForeignKeyViolationError
from pydantic import BaseModel

router = APIRouter(prefix="/tasks",tags=["tasks"])
logger = logging.getLogger(__name__)


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
    role = await get_user_role(conn,task.group_id,current_user["user_id"])
    if role == 'member':
        raise HTTPException(403,"Not authorized")
    await create_group_tasks(conn,task)
    return {"msg":"Tao task thanh cong"}





async def check_assignment_permission(conn, task_id: int, assigner_user_id: int) -> int:
    target_group_id = await task_crud.get_group_id_by_task_id(conn, task_id)
    if target_group_id is None:
        raise HTTPException(status_code=404, detail="Nhiệm vụ không tồn tại.")

    role = await task_crud.check_role(conn, target_group_id, assigner_user_id)
    if role != "leader":
        raise HTTPException(
            status_code=403,
            detail="Chỉ leader của nhóm mới có quyền giao nhiệm vụ này."
        )

    return target_group_id



async def assign_task_to_user_logic(conn, data: TaskAssignmentRequest, current_user_id: int):
    """Logic chính để giao nhiệm vụ."""
    target_group_id = await check_assignment_permission(conn, data.task_id, current_user_id)


    assignee_role = await task_crud.check_role(conn, target_group_id, data.user_id_to_assign)
    if assignee_role is None:
        raise HTTPException(
            status_code=400,
            detail="Người được giao không phải là thành viên của nhóm này."
        )

    is_assigned = await task_crud.check_user_task_exists(conn, data.task_id, data.user_id_to_assign)
    if is_assigned:
        raise HTTPException(status_code=400, detail="Người này đã được giao nhiệm vụ này rồi.")

    try:
        async with conn.transaction():
            assignment = await task_crud.create_users_tasks(
                conn=conn,
                task_id=data.task_id,
                user_id=data.user_id_to_assign,
                comment=data.comment or f"Được giao bởi leader {current_user_id}"
            )
            return assignment

    except asyncpg.UniqueViolationError:
        raise HTTPException(status_code=400, detail="Nhiệm vụ này đã được giao cho người đó.")
    except ForeignKeyViolationError:
        raise HTTPException(status_code=400, detail="Không tìm thấy dữ liệu liên quan trong cơ sở dữ liệu.")
    except Exception as e:
        logger.exception(f"Lỗi khi giao nhiệm vụ {data.task_id}: {e}")
        raise HTTPException(status_code=500, detail="Đã xảy ra lỗi khi giao nhiệm vụ.")



@router.post("/assign", status_code=status.HTTP_201_CREATED)
async def assign_task(
    data: TaskAssignmentRequest,
    current_user=Depends(get_current_user),
    conn = Depends(get_db_conn)
):
    assignment = await assign_task_to_user_logic(conn, data, current_user["user_id"])

    return {
        "msg": f"Đã giao nhiệm vụ {data.task_id} cho người dùng {data.user_id_to_assign} thành công.",
        "assignment": assignment
    }