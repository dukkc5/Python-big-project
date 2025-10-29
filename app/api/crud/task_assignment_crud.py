from datetime import datetime
import asyncpg


async def get_user_tasks(conn: asyncpg.Connection, user_id: int):
    rows = await conn.fetch(
    """
      SELECT
      g.group_name,
    ta.assignment_id,
    t.title AS task_title,
    ta.comment,
    ta.deadline,
    ta.status
    FROM task_assignments ta
    JOIN tasks t ON ta.task_id = t.task_id
    LEFT JOIN groups g ON t.group_id = g.group_id
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
    row = await conn.fetchrow(
    """
        SELECT  assignee_id AS user_id
        FROM task_assignments
        WHERE assignment_id = $1
    """,
    assignment_id
    )
    return dict(row) if row else None

async def update_task_assignment(conn: asyncpg.Connection, assignment_id:int,status:str, deadline:datetime, comment:str):
    row = await conn.fetchrow(
    """
        UPDATE task_assignments
        SET 
            status = $1,
            deadline = $2,
            comment = $3
        WHERE
            assignment_id = $4
        RETURNING assignment_id, task_id, status , deadline , comment;             
    """,status,deadline, comment, assignment_id
    )
    return dict(row) if row else None
async def get_user_related_to_task(conn:asyncpg.Connection,task_id :int):
    rows = await conn.fetch("""
    SELECT
        ta.assignment_id, 
        ta.task_id,        
        ta.assigner_id,        
        u.full_name,      
        ta.comment,        
        ta.status,        
        ta.deadline      
    FROM
        task_assignments ta 
    JOIN
        users u ON ta.assigner_id = u.user_id
    WHERE
        ta.task_id = $1 """,task_id)
    return [row for row in rows]
async def update_assignment_file(conn: asyncpg.Connection, assignment_id: int, file_url: str):
    """
    Cập nhật cột attachment_url cho một assignment cụ thể.
    """
    query = """
        UPDATE task_assignments
        SET attachment_url = $1
        WHERE assignment_id = $2
    """
    try:
        await conn.execute(query, file_url, assignment_id)
        return True
    except Exception as e:
        print(f"Lỗi cập nhật CSDL (attachment_url): {e}")
        return False