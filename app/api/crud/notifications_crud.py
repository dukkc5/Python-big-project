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