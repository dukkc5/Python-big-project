import asyncpg 
from app.models import invitations
#get invitations
async def get_invitations(conn:asyncpg.Connection, user_id:int):
    rows = await conn.fetch("SELECT * FROM group_invitations WHERE recipient_id = $1",user_id)
    return [dict(row) for row in rows]
async def reply_invitations_SQL(conn:asyncpg.Connection, group_id:int , invitation_id :int , reply:str):
    await conn.execute("""UPDATE group_invitations SET status = $1 
            WHERE id = $2 AND group_id = $3""",reply,invitation_id,group_id)
async def send_invitations(conn:asyncpg.Connection, invitation : invitations.Invitations):
    await conn.fetchrow("""
    INSERT INTO group_invitations (group_id ,sender_id,recipient_id,status,title) VALUES ($1,$2,$3,$4,$5)
""",invitation.group_id,invitation.sender_id,invitation.recipient_id,invitation.status,invitation.title)
async def get_invitations_id(conn:asyncpg.Connection,group_id:int ,recipient_id:int):
    row= await conn.fetchrow("""
    SELECT id FROM group_invitations WHERE group_id = $1 AND recipient_id = $2
""",group_id,recipient_id)
    return row["id"] if row else None
async def delete_invitations(conn:asyncpg.Connection,id:int):
    await conn.execute("DELETE FROM group_invitations WHERE id = $1",id)