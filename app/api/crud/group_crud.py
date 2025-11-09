from re import A
import asyncpg
async def get_user_groups(conn: asyncpg.Connection, user_id: int):
    rows = await conn.fetch(
        """
      SELECT * FROM get_user_groups_with_details($1)
        """,
        user_id
    )
    return [dict(row) for row in rows]

async def create_group(conn:asyncpg.Connection, name:str , description:str, owner_id :int): #procedure
     await conn.execute(
        "CALL create_group_with_leader($1, $2, $3);",
        name , description , owner_id
    )
async def add_member(conn: asyncpg.Connection, group_id: int, user_id: int, role: str):
    await conn.execute(
        "INSERT INTO group_members (group_id, user_id, role) VALUES ($1, $2, $3)",  
        group_id, user_id, role
    )
async def get_group_id(conn:asyncpg.Connection , id :int)-> dict:
    row = await conn.fetchrow(
        """
        SELECT * FROM groups WHERE group_id = $1
        """,id
    )
    if row == None:
        return None
    return dict(row)
async def get_user_role(conn : asyncpg.Connection , group_id : int , user_id : int) :
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

async def change_role(conn : asyncpg.Connection, group_id :int , user_id :int , role : str):
    await conn.execute(
    "UPDATE group_members SET role = $1 WHERE group_id=$2 AND user_id = $3",role,group_id,user_id )   
async def get_group_member(conn: asyncpg.Connection , group_id : int):
            rows = await conn.fetch(
                """SELECT 
    u.user_id, 
    u.full_name, 
    u.account, 
    u.avatar_url, 
    gm.role
FROM 
    group_members AS gm
JOIN 
    users AS u ON gm.user_id = u.user_id
WHERE 
    gm.group_id = $1; -- ($1 là group_id)
        """,group_id)                                                                                                                                                                        
            return [dict(row) for row in rows]
async def leave_group(conn:asyncpg.Connection , group_id :int,user_id:int): #procedure
    await conn.execute("""
   CALL leave_group($1, $2)
""",group_id,user_id)