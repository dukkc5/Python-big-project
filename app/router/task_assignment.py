from typing import List
import asyncpg
from fastapi import APIRouter, Depends, HTTPException,status
from websockets import Router

from app.api.crud import task_assignment_crud
from app.api.deps import get_current_user, get_db_conn
from app.api.crud.group_crud import get_user_role
from app.api.crud.task_crud import create_users_tasks, get_group_id_by_task_id
from app.models.task import TaskOut
from app.models.task_assignment import AssignmentUpdate, TaskAssignment, TaskAssignmentOut

router = APIRouter(prefix="/tasks_assignments",tags=["tasks_assignments"])
@router.get("/my-tasks", response_model=List[TaskAssignmentOut])
async def get_my_tasks(
    current_user=Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db_conn)
):
    try:
        tasks = await task_assignment_crud.get_user_tasks(conn, current_user["user_id"])
        return tasks

    except asyncpg.PostgresError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Đã xảy ra lỗi khi lấy danh sách nhiệm vụ: {str(e)}"
        )


 
@router.post("/assign", status_code=status.HTTP_201_CREATED)
async def assign_task(
    assignment : TaskAssignment,
    current_user=Depends(get_current_user),
    conn=Depends(get_db_conn)
):
    try:
        group_id = await get_group_id_by_task_id(conn,assignment.task_id)
        if not group_id:
            raise HTTPException(status_code=404, detail="Không tồn tại nhiệm vụ này")

        check_role = await get_user_role(conn, group_id, assignment.user_id)
        if not check_role:
            raise HTTPException(status_code=404, detail="Không có user này trong nhóm")

        role = await get_user_role(conn, group_id, current_user["user_id"])
        if role == "member":
            raise HTTPException(status_code=403, detail="Không có quyền giao nhiệm vụ")

        await create_users_tasks(conn,assignment.task_id, assignment.user_id,current_user["user_id"], assignment.comment,assignment.deadline)

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


@router.delete("/{assignment_id}", status_code=status.HTTP_200_OK)
async def delete_task_member(
    assignment_id : int,
    conn:asyncpg.Connection = Depends(get_db_conn),
    current_user = Depends(get_current_user)
    
):
    assignment = await task_assignment_crud.get_assignment_by_id(conn,assignment_id)
    if not assignment:
        raise HTTPException(status_code=404,detail="Không tìm thấy nhiệm vụ được giao")
    
    task_id = assignment["task_id"]
    group_id = await task_assignment_crud.get_group_id_by_task_id(conn,task_id)
    if not group_id:
        raise  HTTPException(status_code=404, detail="Không tìm thấy nhóm chứa nhiệm vụ này")
    
    role = await get_user_role(conn,group_id,current_user["user_id"])
    if role != 'leader':
        raise HTTPException(status_code=403, detail="Chỉ leader mới được xóa nhiệm vụ này") 
    await task_assignment_crud.delete_assignment(conn,assignment_id)
    
    return {"message": "Xóa nhiệm vụ thành công"}

@router.put("/{assignment_id}", status_code=status.HTTP_200_OK)
async def update_task_assignment(
    assignment_id : int, 
    data : AssignmentUpdate,
    conn: asyncpg.Connection = Depends(get_db_conn),
    current_user = Depends(get_current_user)    
):
    record = await task_assignment_crud.get_user_id_by_assignment_id(conn,assignment_id)
    
    if not record:
        raise HTTPException(status_code=404,detail="Không tìm thấy nhiệm vụ.")
    if record["user_id"] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Bạn không có quyền sửa nhiệm vụ này.")
    
    update = await task_assignment_crud.update_task_assignment(
        conn,
        assignment_id,
        data.status,
        data.deadline, 
        data.comment 
    )
    if not update:
        raise HTTPException(status_code=400, detail="Cập nhật thất bại.")
    return {"message": "Cập nhật nhiệm vụ cá nhân thành công", "assignment": update}
@router.get("/list/{task_id}")
async def get_list_user(task_id :int ,conn: asyncpg.Connection = Depends(get_db_conn),
    current_user = Depends(get_current_user)):
    return await task_assignment_crud.get_user_related_to_task(conn,task_id)