import datetime
from re import A
import asyncpg
import asyncpg

from app.models.task import TaskCreate

async def get_group_tasks(conn: asyncpg.Connection, group_id: int):
    rows = await conn.fetch(
    """
    SELECT t.task_id,t.title,t.description,t.status,t.deadline
    FROM tasks t
    WHERE group_id = $1
    """,group_id
    )
    return [dict(row) for row in rows]

async def create_group_tasks(conn: asyncpg.Connection, task:TaskCreate):
    rows = await conn.fetchrow(
    """
    INSERT INTO tasks(group_id,title,description,deadline)  
    VALUES ($1,$2,$3,$4) RETURNING *
    """,task.group_id,task.title,task.description,task.deadline
    )
    return dict(rows)
 
async def get_group_id_by_task_id(conn: asyncpg.Connection, task_id:int):
    row = await conn.fetchrow(
        "SELECT group_id FROM tasks WHERE task_id = $1", 
        task_id
    )  
    return row['group_id'] if row else None

async def create_users_tasks(conn: asyncpg.Connection, 
                             task_id : int,
                             assigner_id: int,
                             assignee_id: int,
                             comment : str,
                             deadline : datetime):
   await conn.execute(
    """
    INSERT INTO task_assignments (task_id,assigner_id,assignee_id, comment,deadline)
    VALUES ($1,$2,$3,$4,$5)
    """,task_id,assigner_id,assignee_id,comment,deadline
    )
   
async def remove_task_id(conn: asyncpg.Connection, task_id: int):
    rows =  await conn.fetchrow("DELETE FROM tasks WHERE task_id =$1 RETURNING * ",task_id)
    return dict(rows) 
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

    
    