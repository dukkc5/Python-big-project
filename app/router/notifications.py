from anyio import current_effective_deadline
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import asyncpg
from datetime import datetime

from app.api.crud import notifications_crud
from app.api.crud.notifications_crud import create_notification,get_notification
from app.models.notification import NotificationOut
from app.router.auth import get_user_by_account
from app.config.db import get_db
from app.api.deps import get_current_user, get_db_conn,check_user_role
from app.api.crud.group_crud import get_group_id,get_user_role
from asyncpg.exceptions import ForeignKeyViolationError
from pydantic import BaseModel
from asyncpg import PostgresError, exceptions

from app.api.crud.notifications_crud import get_notification
    

router = APIRouter(prefix="/notifications",tags=["notifications"])
@router.get("/", response_model=List[NotificationOut])
async def read_notifications(
    current_user=Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db_conn)
):
    try:
        rows = await get_notification(conn, current_user["user_id"])

        notifications = []
        for row in rows:
            message = f"Leader {row['leader_name']} đã giao nhiệm vụ {row['task_id']} cho bạn."
            notifications.append({
                "notification_id": row["notification_id"],
                "message": message,
                "created_at": row["created_at"]
            })

        return notifications

    except asyncpg.PostgresError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Đã xảy ra lỗi khi đọc thông báo: {str(e)}"
        )
