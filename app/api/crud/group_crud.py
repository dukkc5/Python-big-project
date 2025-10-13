from re import A
import asyncpg
async def get_user_groups(conn: asyncpg.Connection, user_id: int):
    rows = await conn.fetch(
        """
        SELECT g.group_id, g.group_name, g.description
        FROM groups g
        JOIN group_members gm ON g.group_id = gm.group_id
        WHERE gm.user_id = $1
        """,
        user_id
    )
    return [dict(row) for row in rows]
async def create_group(conn:asyncpg.Connection, name:str , description:str, owner_id :int):
    row = await conn.fetchrow(
        "INSERT INTO groups (group_name , description , owner_id) VALUES ($1,$2,$3) RETURNING group_id",
        name , description , owner_id
    )
    return row["group_id"]
async def add_member(conn: asyncpg.Connection, group_id: int, user_id: int, role: str):
    await conn.execute(
        "INSERT INTO group_members (group_id, user_id, role) VALUES ($1, $2, $3)",
        group_id, user_id, role
    )
async def get_group_id(conn : asyncpg.Connection,id :int):
    row = await conn.fetchrow(
        """
    SELECT * FROM groups WHERE group_id = $1
""",id
    )
    if row == None:
        return None
    return dict(row)
async def get_user_role(conn : asyncpg.Connection , group_id : int , user_id : int):
    row = await conn.fetchrow(
        """
    SELECT role FROM group_members WHERE group_id = $1 AND user_id = $2
""",group_id,user_id
    )
    return row["role"] if row else None
async def remove_member(conn : asyncpg.Connection , group_id:int , user_id:int , ):
    await conn.execute(
        "DELETE FROM group_members WHERE group_id = $1 AND user_id = $2",group_id,user_id
    )
async def delete_group(conn:asyncpg.Connection,group_id:int):
    await conn.execute("DELETE FROM groups WHERE group_id =$1",group_id)
