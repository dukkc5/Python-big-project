import logging  # Thêm logging
from operator import imod
from pstats import Stats
from typing import List

import asyncpg
from asyncpg.exceptions import (  # Thêm các exception CSDL
    DataError,
    ForeignKeyViolationError,
    UniqueViolationError,
)
from click import group
from fastapi import APIRouter, Depends, HTTPException, status  # Thêm status
from httpx import get
from pydantic import EmailStr

from app.api.crud import group_crud, invitations_crud
from app.api.crud.group_crud import (
    add_member,
    change_role,
    create_group,
    get_group_id,
    get_user_groups,
    get_user_role,
)
from app.api.crud.user_crud import get_user_by_email
from app.api.deps import get_current_user, get_db_conn
from app.config.db import get_db
from app.models import invitations
from app.models.group import GroupCreate, GroupOut, MemberAdd, MemberToLeader

router = APIRouter(prefix="/groups", tags=["groups"])


@router.get("/", response_model=List[GroupOut])
async def read_user_groups(
    current_user=Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db_conn),
):
    try:
        return await get_user_groups(conn, current_user["user_id"])
    except Exception as e:
        logging.error(f"Lỗi 500 khi read_user_groups: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Có lỗi hệ thống xảy ra.",
        )


@router.post("/", response_model=GroupOut)
async def create_group_route(
    group: GroupCreate,
    current_user=Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db_conn),
):
    try:
        group_id = await create_group(
            conn, group.group_name, group.description, current_user["user_id"]
        )
        await add_member(conn, group_id, current_user["user_id"], "leader")
        return {
            "group_id": group_id,
            "group_name": group.group_name,
            "description": group.description,
        }
    except UniqueViolationError:
        # Giả sử group_name là UNIQUE
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Tên nhóm này đã tồn tại.",
        )
    except DataError as e:
        # Tên hoặc mô tả quá dài
        logging.warning(f"Lỗi DataError khi create_group: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Dữ liệu không hợp lệ: {e}",
        )
    except Exception as e:
        logging.error(f"Lỗi 500 khi create_group_route: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Có lỗi hệ thống xảy ra.",
        )


@router.get("/{group_id}")
async def get_group(
    group_id: int,
    current_user=Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db_conn),
):
    try:
        group = await get_group_id(conn, group_id)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Nhóm này không tồn tại"
            )
        
        role = await get_user_role(conn, group_id, current_user["user_id"])
        if not role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không phải là thành viên của nhóm này",
            )
        return group
    except Exception as e:
        logging.error(f"Lỗi 500 khi get_group: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Có lỗi hệ thống xảy ra.",
        )


@router.delete("/{group_id}/members/{email}")
async def delete_member(
    group_id: int,
    email: EmailStr,
    current_user=Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db_conn),
):
    try:
        user = await get_user_by_email(conn, email)
        if not user:
            # Đây là lỗi logic bạn đã bỏ sót, tôi thêm vào
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Email này không tồn tại"
            )

        if not await get_group_id(conn, group_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Nhóm này không tồn tại"
            )

        role = await get_user_role(conn, group_id, user["user_id"])
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Thành viên này không có trong nhóm",
            )

        role_current = await get_user_role(conn, group_id, current_user["user_id"])
        if role_current == "member":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Bạn không có quyền này"
            )

        if role == "leader":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Leader không thể rời nhóm (cần chuyển quyền trước)",
            )
            
        await group_crud.remove_member(conn, group_id, user["user_id"])
        return {"msg": "Xóa thành viên thành công"}
        
    except Exception as e:
        logging.error(f"Lỗi 500 khi delete_member: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Có lỗi hệ thống xảy ra.",
        )


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(
    group_id: int,
    current_user=Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db_conn),
):
    try:
        if not await get_group_id(conn, group_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Nhóm này không tồn tại"
            )

        role = await get_user_role(conn, group_id, current_user["user_id"])
        if not role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có trong nhóm này",
            )

        if role != "leader":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Không có quyền xóa nhóm"
            )

        await group_crud.delete_group(conn, group_id)
        # Khi dùng 204 NO CONTENT, bạn không nên trả về body
        return 

    except ForeignKeyViolationError:
        # Lỗi này xảy ra khi bạn cố xóa nhóm nhưng vẫn còn
        # thành viên, task... liên quan (và CSDL không set ON DELETE CASCADE)
        logging.warning(f"Lỗi 409 khi delete_group: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Không thể xóa nhóm, vẫn còn dữ liệu liên quan (thành viên, nhiệm vụ...).",
        )
    except Exception as e:
        logging.error(f"Lỗi 500 khi delete_group: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Có lỗi hệ thống xảy ra.",
        )


@router.post("/{group_id}/members", status_code=status.HTTP_201_CREATED)
async def add_new_member(
    group_id: int,
    user_add: MemberAdd,
    conn: asyncpg.Connection = Depends(get_db_conn),
    current_user=Depends(get_current_user),
):
    try:
        find_group = await get_group_id(conn, group_id)
        if not find_group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy nhóm này"
            )

        user = await get_user_by_email(conn, user_add.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User này không tồn tại"
            )

        role_of_user = await get_user_role(conn, group_id, user["user_id"])
        if role_of_user: # Chỉ cần check `if role_of_user` là đủ
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, # 409 (Conflict) thì đúng hơn 302
                detail="Thành viên này đã ở trong nhóm",
            )

        role = await get_user_role(conn, group_id, current_user["user_id"])
        if not role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có trong nhóm này",
            )
        if role == "member":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền, không thể thêm thành viên",
            )

        invitation = invitations.Invitations(
            title=f"{current_user['full_name']} mời bạn vào nhóm {find_group['group_name']}",
            group_id=group_id,
            sender_id=current_user["user_id"],
            recipient_id=user["user_id"],
            status="pending",
        )
        
        id = await invitations_crud.get_invitations_id(
            conn, group_id, user["user_id"]
        )
        if id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, # 409 (Conflict) thì đúng hơn 303
                detail="Bạn đã gửi lời mời cho user này rồi",
            )
            
        await invitations_crud.send_invitations(conn, invitation)
        return {"msg": "Đã gửi lời mời thành công"}

    except (UniqueViolationError, ForeignKeyViolationError) as e:
        # Bắt lỗi nếu gửi invitation bị lỗi CSDL
        logging.warning(f"Lỗi 422 khi add_new_member: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Lỗi CSDL khi tạo lời mời.",
        )
    except Exception as e:
        logging.error(f"Lỗi 500 khi add_new_member: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Có lỗi hệ thống xảy ra.",
        )


@router.post("/{group_id}/members/{user_id}")
async def make_member_to_leader(
    group_id: int,
    user_to_leader: MemberToLeader,
    conn: asyncpg.Connection = Depends(get_db_conn),
    current_user=Depends(get_current_user),
):
    try:
        user = await get_user_by_email(conn, user_to_leader.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User này không tồn tại"
            )

        if not await get_group_id(conn, group_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Nhóm này không tồn tại"
            )

        role = await get_user_role(conn, group_id, current_user["user_id"])
        if not role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không ở trong nhóm này",
            )

        if role == "member":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Bạn không có quyền này"
            )

        # Thêm check: user được chuyển quyền phải là member
        role_user_to_leader = await get_user_role(conn, group_id, user["user_id"])
        if not role_user_to_leader:
             raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User bạn muốn chuyển quyền không ở trong nhóm này",
            )
        
        # Cập nhật quyền
        await change_role(conn, group_id, user["user_id"], "leader")
        await change_role(conn, group_id, current_user["user_id"], "member")
        
        return {"msg": "Chuyển quyền leader thành công"}

    except Exception as e:
        logging.error(f"Lỗi 500 khi make_member_to_leader: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Có lỗi hệ thống xảy ra.",
        )