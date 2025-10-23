from operator import imod
import asyncpg
from fastapi import Depends, FastAPI , APIRouter, HTTPException, status # Thêm status
import logging # Thêm logging

# Thêm các exception cụ thể từ asyncpg
from asyncpg.exceptions import ForeignKeyViolationError, UniqueViolationError

from app.api.crud.group_crud import add_member, get_group_id
from app.api.crud.invitations_crud import delete_invitations, get_invitations , reply_invitations_SQL
from app.api.deps import get_current_user, get_db_conn

router = APIRouter(prefix="/invitations",tags=["Invitations"])

@router.get("/")
async def get_user_invitations(
    current_user = Depends(get_current_user),
    conn:asyncpg.Connection = Depends(get_db_conn)
):
    """
    Lấy tất cả lời mời của user hiện tại.
    """
    try:
        return await get_invitations(conn,current_user["user_id"])
    
    except Exception as e:
        logging.error(f"Lỗi 500 khi get_user_invitations: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Có lỗi hệ thống xảy ra."
        )

@router.put("/reply_invitations/{invitation_id}")
async def reply_invitations(
    group_id:int,
    reply:str,
    invitation_id :int,
    current_user = Depends(get_current_user),
    conn:asyncpg.Connection=Depends(get_db_conn)
):
    """
    Trả lời một lời mời (accepted hoặc declined).
    Bao gồm nhiều thao tác CSDL nên cần được bảo vệ cẩn thận.
    """
    if reply.lower() not in ("accepted","rejected"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Giá trị 'reply' chỉ có thể là 'accepted' hoặc 'rejected'"
        )
    elif not reply:
        raise HTTPException(404,"This invitation not exist")

    try:
        await reply_invitations_SQL(conn, group_id, invitation_id, reply)
        
        if reply.lower() == "accepted":
            await add_member(conn, group_id, current_user["user_id"], "member")

        await delete_invitations(conn, invitation_id)        
        return {"msg": f"Đã {reply} "}

    except ForeignKeyViolationError:
        logging.warning(f"Lỗi 404 khi reply_invitations: group_id hoặc user_id không tồn tại.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group hoặc User không tồn tại trong CSDL."
        )
        
    except UniqueViolationError:
        logging.warning(f"Lỗi 409 khi reply_invitations: User {current_user['user_id']} đã ở trong nhóm {group_id}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bạn đã là thành viên của nhóm này."
        )
    except Exception as e:
        logging.error(f"Lỗi 500 khi reply_invitations: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Có lỗi hệ thống xảy ra."
        )