from logging import raiseExceptions
from pstats import Stats
from typing import List
import asyncpg
from click import group
from fastapi import APIRouter, Depends, HTTPException , status
from httpx import get
from pydantic import EmailStr
from app.api.crud import group_crud, invitations_crud
from app.api.crud.group_crud import  add_member, create_group, get_group_id, get_user_groups, get_user_role,change_role
from app.api.crud.user_crud import get_user_by_email
from app.api.deps import get_current_user, get_db_conn
from app.config.db import get_db
from app.models import invitations
from app.models.group import GroupCreate, GroupOut,MemberAdd, MemberToLeader
router = APIRouter(prefix="/groups",tags=["groups"])
@router.get("/", response_model=List[GroupOut])
async def read_user_groups(
    current_user = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db_conn)
):
    return await get_user_groups(conn, current_user["user_id"])
@router.post("/",response_model=GroupOut)
async def create_group_route(
    group:GroupCreate,
    current_user = Depends(get_current_user),
    conn:asyncpg.Connection= Depends(get_db_conn)
):
    group_id = await create_group(conn,group.group_name,group.description,current_user["user_id"])
    await add_member(conn,group_id,current_user["user_id"],"leader")
    return {"group_id": group_id, "group_name": group.group_name, "description": group.description}
@router.get("/{group_id}")
async def get_group(
    group_id : int,
    current_user = Depends(get_current_user),
    conn:asyncpg.Connection= Depends(get_db_conn)
):
    group = await get_group_id(conn,group_id)
    if not group:
        raise HTTPException(404,"This Group not exist")
    role = await get_user_role(conn,group_id,current_user["user_id"])
    if not role:
        raise HTTPException(status.HTTP_403_FORBIDDEN,"You are not a member of this group")
    return group
@router.delete("/{group_id}/members/{email}")
async def delete_member(
    group_id :int,
    email : EmailStr,
    current_user = Depends(get_current_user),
    conn:asyncpg.Connection = Depends(get_db_conn)
):
    user = await get_user_by_email(conn,email)
    if not await get_group_id(conn,group_id):
        raise HTTPException(404 ,"this group not exist")
    role = await get_user_role(conn,group_id,user["user_id"])
    if not role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="this member not in this group")
    role_current = await get_user_role(conn,group_id,current_user["user_id"])
    if role_current == "member":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="you not authorized")
    if role == "leader":
        raise HTTPException(403,"Leader can't leave this group")
    await group_crud.remove_member(conn,group_id,user["user_id"])
@router.delete("/{group_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(
    group_id : int,
    current_user = Depends(get_current_user),
    conn:asyncpg.Connection = Depends(get_db_conn)
):
    if not await get_group_id(conn,group_id):
        raise HTTPException(404,"this group does not exist")
    role = await get_user_role(conn,group_id,current_user["user_id"])
    if not role:
        raise HTTPException(404,"you are not in this group")
    if role != "leader":
        raise HTTPException(404,"not aurthorize")
    await group_crud.delete_group(conn, group_id)
    return {"Msg":"delete successfully"}
@router.post("/{group_id}/members",status_code=status.HTTP_201_CREATED)
async def add_new_member(
    group_id : int,
    user_add : MemberAdd,
    conn : asyncpg.Connection = Depends(get_db_conn),
    current_user = Depends(get_current_user)
):
    find_group = await get_group_id(conn,group_id)
    if not find_group:
        raise HTTPException(404,"Not Found This Group")
    user = await get_user_by_email(conn,user_add.email)
    if not user:
        raise HTTPException(404,"This user does not exist")
    role_of_user = await get_user_role(conn,group_id,user["user_id"])
    if role_of_user =="member":
        raise HTTPException(status_code=status.HTTP_302_FOUND,detail="this member is being in this group")
    role = await get_user_role(conn,group_id,current_user["user_id"])
    if not role:
        raise HTTPException(404,"You are not in this group")
    if role == "member":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,"you are not leader , cant add new member")
    
    invitation = invitations.Invitations(title=f"{current_user['full_name']} invite you to the group {find_group['group_name']}",
                                         group_id=group_id,
                                         sender_id=current_user["user_id"],
                                         recipient_id=user["user_id"],
                                         status="pending")
    id = await invitations_crud.get_invitations_id(conn,group_id,user["user_id"])
    if id:
        raise HTTPException(303,"You've already invited to this user")
    await invitations_crud.send_invitations(conn,invitation)
    return {"msg":"sent invitation successfully"}
@router.post("/{group_id}/members/{user_id}")
async def make_member_to_leader(
    group_id:int,
    user_to_leader:MemberToLeader,
    conn:asyncpg.Connection=Depends(get_db_conn),
    current_user = Depends(get_current_user)
):
    
    user = await get_user_by_email(conn,user_to_leader.email)
    if not user:
        raise HTTPException(404,"This user does not exist")
    if not await get_group_id(conn,group_id):
        raise HTTPException(404,"This group does not exist")
    # vao dc group
    role = await get_user_role(conn,group_id,current_user["user_id"])
    if not role :
        raise HTTPException(404,"This member is not in this group")
    if role =="member":
        raise HTTPException(403,"You can't change")
    await change_role(conn,group_id,user["user_id"],"leader")
    await change_role(conn,group_id,current_user["user_id"],"member")
    
    
    
        

