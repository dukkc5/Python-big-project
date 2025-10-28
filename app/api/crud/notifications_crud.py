import asyncpg


async def create_notification(conn:asyncpg.Connection, user_id:int, message:str,
                              type: str = None, task_id: int = None):
    row = await conn.fetchrow(
    """
    INSERT INTO notifications (user_id, message,type,task_id)
    VALUES ($1,$2,$3,$4)
    RETURNING *
    """,user_id,message,type,task_id
    )   
    return dict(row)

async def get_notification(conn: asyncpg.Connection, user_id: int):
    rows = await conn.fetch(
    """
       SELECT 
            n.notification_id,
            n.user_id,
            n.task_id,
            n.created_at,
            u.full_name AS leader_name
        FROM notifications n
        JOIN tasks t ON n.task_id = t.task_id
        JOIN groups g ON t.group_id = g.group_id
        JOIN group_member gm ON g.group_id = gm.group_id
        JOIN users u ON gm.user_id = u.id
        WHERE 
            n.user_id = $1
            AND gm.role = 'leader'
        ORDER BY n.created_at DESC;
    """,
    user_id
    )
    return [dict(row) for row in rows]
