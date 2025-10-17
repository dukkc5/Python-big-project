from re import A
import asyncpg
import asyncpg

async def get_group_tasks(conn: asyncpg.Connection, group_id: int):
    rows = await conn.fetch(
    """
    SELECT t.title,t.description 
    FROM tasks t
    WHERE group_id = $1
    """,group_id
    )
    return [dict(row) for row in rows]

    