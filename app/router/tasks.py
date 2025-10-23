
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import asyncpg
from datetime import datetime

from app.api.crud import task_crud
from app.api.crud.task_crud import create_group_tasks, create_users_tasks, get_group_id_by_task_id, get_group_tasks
from app.models.task import TaskAssignmentRequest, TaskOut, TaskCreate, TaskUpdate
from app.router.auth import get_user_by_account
from app.api.deps import get_current_user, get_db_conn,check_user_role
from app.api.crud.group_crud import get_group_id,get_user_role
from asyncpg.exceptions import ForeignKeyViolationError
from pydantic import BaseModel
from asyncpg import PostgresError, exceptions

router = APIRouter(prefix="/tasks",tags=["tasks"])


@router.get("/", response_model=List[TaskOut])
async def read_group_tasks(
    group_id: int,
    current_user=Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db_conn)
):
    try:
        if not await get_group_id(conn, group_id):
            raise HTTPException(status_code=404, detail="This group not found")
        await check_user_role(conn, group_id, current_user["user_id"])
        tasks = await get_group_tasks(conn, group_id)
        return tasks

    except asyncpg.PostgresError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.post("/", status_code=200)
async def create_group_task(
    task: TaskCreate,
    current_user=Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db_conn)
):
    creator_user_id = current_user["user_id"]

    try:

        if not await get_group_id(conn, task.group_id):
            raise HTTPException(status_code=404, detail="This group not found")

        role = await get_user_role(conn, task.group_id, creator_user_id)
        if role == "member":
            raise HTTPException(status_code=403, detail="Not authorized")

        await create_group_tasks(conn, task)

        return {"msg": "Tạo task thành công"}

    except asyncpg.PostgresError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post("/assign", status_code=status.HTTP_201_CREATED)
async def assign_task(
    task_id: int,
    user_id: int,
    current_user=Depends(get_current_user),
    conn=Depends(get_db_conn)
):
    try:
        group_id = await get_group_id_by_task_id(conn, task_id)
        if not group_id:
            raise HTTPException(status_code=404, detail="Không tồn tại nhiệm vụ này")

        check_role = await get_user_role(conn, group_id, user_id)
        if not check_role:
            raise HTTPException(status_code=404, detail="Không có user này trong nhóm")

        role = await get_user_role(conn, group_id, current_user["user_id"])
        if role == "member":
            raise HTTPException(status_code=403, detail="Không có quyền giao nhiệm vụ")

        await create_users_tasks(conn, task_id, user_id, "do this task")

        return {"msg": "Giao nhiệm vụ thành công"}

    except exceptions.UniqueViolationError:
        raise HTTPException(status_code=400, detail="Người này đã được giao task này rồi")

    except PostgresError as e:
        raise HTTPException(status_code=500, detail=f"Lỗi cơ sở dữ liệu: {str(e)}")

    except HTTPException:
        raise 

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi không xác định: {str(e)}")


from asyncpg import PostgresError, exceptions

@router.delete("/{task_id}", status_code=status.HTTP_200_OK)
async def delete_task(
    group_id: int,
    task_id: int,
    current_user=Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db_conn)
):
    try:
        if not await get_group_id(conn, group_id):
            raise HTTPException(status_code=404, detail="This group does not exist")
        role = await get_user_role(conn, group_id, current_user["user_id"])
        if not role:
            raise HTTPException(status_code=403, detail="You are not in this group")
        if role != "leader":
            raise HTTPException(status_code=403, detail="Not authorized")

        deleted = await task_crud.remove_task_id(conn, task_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Task not found")

        return {"message": "Deleted successfully"}

    except exceptions.ForeignKeyViolationError:
        raise HTTPException(status_code=400, detail="Cannot delete task — it's linked to other records")
    except PostgresError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except HTTPException:
        raise 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.put("/{task_id}", response_model=TaskOut)
async def update_task(
    group_id: int,
    task_id: int,
    task_data: TaskUpdate,
    current_user=Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db_conn),
):
    try:
        if not await get_group_id(conn, group_id):
            raise HTTPException(404, "Group not found")
        task_group_id = await get_group_id_by_task_id(conn, task_id)
        if not task_group_id:
            raise HTTPException(404, "Task not found")
        if task_group_id != group_id:
            raise HTTPException(400, "Task does not belong to this group")
        role = await get_user_role(conn, group_id, current_user["user_id"])
        if not role:
            raise HTTPException(403, "You are not in this group")
        if role != "leader":
            raise HTTPException(403, "Permission denied")
        updated = await task_crud.update_task(conn, task_id, task_data)
        if not updated:
            raise HTTPException(404, "Task not found")
        return dict(updated)
    except asyncpg.PostgresError as e:
        raise HTTPException(500, f"Database error: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Unexpected error: {str(e)}")




