from datetime import datetime
import asyncpg


async def get_user_tasks(conn: asyncpg.Connection, user_id: int):
    rows = await conn.fetch(
    """
        SELECT 
            ta.assignment_id,
            t.task_id,
            t.title AS task_title,
            t.description,
            t.status AS task_status,
            ta.status AS assignment_status,
            u.full_name AS assigner_name,
            ta.comment,
            ta.created_at AS assigned_at
        FROM task_assignments ta
        JOIN tasks t ON ta.task_id = t.task_id
        JOIN users u ON ta.assigner_id = u.user_id
        WHERE ta.assignee_id = $1
        ORDER BY ta.created_at DESC;
    """,user_id
    )
    return [dict(row) for row in rows]

async def get_assignment_by_id(conn: asyncpg.Connection, assignment_id: int):
    row = await conn.fetchrow(
         "SELECT * FROM task_assignments WHERE assignment_id = $1", 
         assignment_id
    )  
    return dict(row) if row else None
     
     
async def delete_assignment(conn: asyncpg.Connection, assignment_id : int):
      await conn.execute(
        "DELETE FROM task_assignments WHERE assignment_id = $1",
        assignment_id
     )         
    
async def get_group_id_by_task_id(conn: asyncpg.Connection, task_id: int):
    row = await conn.fetchrow(
        "SELECT group_id FROM tasks WHERE task_id = $1;",
        task_id
    )
    return row["group_id"] if row else None

async def get_user_id_by_assignment_id(conn:asyncpg.Connection, assignment_id:int):
    rows = await conn.fetch(
    """
        SELECT  assignee_id AS user_id
        FROM task_assignments
        WHERE assignment_id = $1
    """,
    assignment_id
    )
    return dict(rows) if rows else None

async def update_task_assignment(conn: asyncpg.Connection, assignment_id:int,status:str,deadline, comment:str):
    rows = await conn.fetch(
    """
        UPDATE task_assignments
        SET 
            status = $1,
            deadline = $2,
            comment = $3,
        WHERE
            assignment_id = $4
        RETURNING assignment_id, task_id, user_id, status , deadline , comment;             
    """,status,deadline, comment, assignment_id
    )
    return dict(rows) if rows else None
