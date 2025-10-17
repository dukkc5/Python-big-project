from operator import imod
import asyncpg
from fastapi import Depends, FastAPI , APIRouter, HTTPException

from app.api.crud.group_crud import add_member, get_group_id
from app.api.crud.invitations_crud import delete_invitations, get_invitations , reply_invitations_SQL
from app.api.deps import get_current_user, get_db_conn
router = APIRouter(prefix="/invitations",tags=["Invitations"])
@router.get("/")
async def get_user_invitations(
    current_user = Depends(get_current_user),
    conn:asyncpg.Connection = Depends(get_db_conn)
):
    return await get_invitations(conn,current_user["user_id"])
@router.put("/reply_invitations/{invitation_id}")
async def reply_invitations(
    group_id:int,
    reply:str,
    invitation_id :int,
    current_user = Depends(get_current_user),
    conn:asyncpg.Connection=Depends(get_db_conn)
):
    
    await reply_invitations_SQL(conn,group_id,invitation_id,reply)
    if reply == "accepted":
        await add_member(conn,group_id,current_user["user_id"],"member")
    await delete_invitations(conn,invitation_id)
    

    