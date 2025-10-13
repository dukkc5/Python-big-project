from pstats import Stats
from typing import List
import asyncpg
from fastapi import APIRouter, Depends, HTTPException , status
from httpx import get
from app.api.crud import group_crud
from app.api.crud.group_crud import add_member, create_group, get_group_id, get_user_groups, get_user_role
from app.api.deps import get_current_user, get_db_conn
from app.config.db import get_db
from app.models.group import GroupCreate, GroupOut

router = APIRouter(prefix="/groups",tags=["groups"])
@router.get("/", response_model=List[GroupOut])
async def read_user_groups(
    current_user = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db_conn)
):
    return await get_user_groups(conn, current_user["user_id"])
@router.post("/create_group",response_model=GroupOut)
async def create_group_route(
    group:GroupCreate,
    current_user = Depends(get_current_user),
    conn:asyncpg.Connection= Depends(get_db_conn)
):
    group_id = await create_group(conn,group.group_name,group.description,current_user["user_id"])
    await add_member(conn,group_id,current_user["user_id"],role="leader")
    return {"group_id": group_id, "group_name": group.group_name, "description": group.description}
@router.get("/get_group_id/{group_id}")
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
@router.delete("/delete_member/{id}")
async def delete_member(
    group_id :int,
    user_deleted_id : int = id,
    current_user = Depends(get_current_user),
    conn:asyncpg.Connection = Depends(get_db_conn)
):
    if not await get_group_id(conn,group_id):
        raise HTTPException(404 ,"this group not exist")
    role = await get_user_role(conn,group_id , current_user)
    if not role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="you not in this group")
    if role != "leader":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="you not authorized")
    await group_crud.remove_member(conn,group_id,user_deleted_id)
@router.delete("/delete_group",status_code=status.HTTP_204_NO_CONTENT)
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

    

