from re import A
import asyncpg
import asyncpg

from app.models.task import TaskCreate

async def get_group_tasks(conn: asyncpg.Connection, group_id: int):
    rows = await conn.fetch(
    """
    SELECT t.title,t.description 
    FROM tasks t
    WHERE group_id = $1
    """,group_id
    )
    return [dict(row) for row in rows]

async def create_group_tasks(conn: asyncpg.Connection, task:TaskCreate):
    rows = await conn.fetchrow(
    """
    INSERT INTO tasks(group_id,title,description,deadline)  
    VALUES ($1,$2,$3,$4)
    """,task.group_id,task.title,task.description,task.deadline
    )
 
async def get_group_id_by_task_id(conn: asyncpg.Connection, task_id:int):
    row = await conn.fetchrow(
        "SELECT group_id FROM tasks WHERE task_id = $1", 
        task_id
    )  
    return row['group_id'] if row else None

async def create_users_tasks(conn: asyncpg.Connection, 
                             task_id : int,
                             user_id : int,
                             comment : str):
   await conn.execute(
    """
    INSERT INTO task_assignments (task_id, user_id, comment)
    VALUES ($1,$2,$3)
    """,task_id,user_id,comment
    )
   
async def remove_task_id(conn: asyncpg.Connection, task_id: int):
    await conn.execute("DELETE FROM tasks WHERE task_id =$1",task_id)
    
async def update_task(conn, task_id, task_data):
    row = await conn.fetchrow(
        """
        UPDATE tasks
        SET title = $1, description = $2, deadline = $3, status = $4
        WHERE task_id = $5
        RETURNING *
        """,
        task_data.title, task_data.description, task_data.deadline, task_data.status, task_id
    )
    return row
    
    