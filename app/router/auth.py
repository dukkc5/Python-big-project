from enum import verify
from venv import create
from fastapi import APIRouter, Depends, HTTPException ,status
from fastapi.security import OAuth2
from websockets import Router
import asyncpg
from app.api.crud.user_crud import create_user, get_user_by_email
from app.api.deps import get_db_conn
from app.models import user 
from app.config.security import verify_password,create_acess_token
from jose import jwt , JWTError

router = APIRouter(prefix="/auth" ,tags=["auth"])
@router.post("/register",status_code=status.HTTP_201_CREATED) #decorator 
async def register(user: user.UserCreate,conn:asyncpg.Connection=Depends(get_db_conn)):
    db_user = await get_user_by_email(conn,user.email)
    if db_user:
        raise HTTPException(400,"Email already registered")
    await create_user(conn,user.email,user.password,user.full_name)
    return {"msg":"User created"}
@router.post("/login")
async def login(user: user.UserLogin, conn:asyncpg.Connection=Depends(get_db_conn)):
    db_user = await get_user_by_email(conn,user.email)
    if not db_user: # compare email
        raise HTTPException(404,"Incorect email or password")
    if not verify_password(user.password,db_user["password_hash"]): #compare passw
        raise HTTPException(404,"Incorect email or password")
    access_token = create_acess_token(data={"sub":db_user["email"]}) # token chua thong tin cua user da login thanh cong
    return {"access_token":access_token,"token_type":"bearer"}
    
    
    