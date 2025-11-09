
import asyncpg
from typing import List, Dict, Any

async def get_notifications_by_user(
    conn: asyncpg.Connection, 
    user_id: int
) -> List[asyncpg.Record]:
    """Lấy tất cả thông báo của user từ CSDL."""

    rows = await conn.fetch("SELECT notification_id, user_id, message, created_at FROM notifications WHERE user_id = $1 ORDER BY created_at DESC" , user_id)
    return [dict(row) for row in rows]

# ===== XÓA =====
async def delete_all_notifications_by_user(
    conn: asyncpg.Connection, 
    user_id: int
) -> bool:
    """Xóa tất cả thông báo của user."""
    
    query = "DELETE FROM notifications WHERE user_id = $1"
    
    try:
        await conn.execute(query, user_id)
        return True
    except Exception as e:
        print(f"Lỗi DB [delete_all_notifications_by_user]: {e}")
        return False