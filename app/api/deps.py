import asyncpg
from fastapi import Depends 
from fastapi import security,HTTPException
from app.api.crud.group_crud import get_user_role
from app.config.db import get_db
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from jose import JWTError , jwt
from app.api.crud.user_crud import get_user_by_account
security =  HTTPBearer()
from app.config.config import settings

async def get_db_conn():
    async with get_db() as conn:
        await conn.execute("SET TIMEZONE TO 'Asia/Ho_Chi_Minh'")
        yield conn
async def get_current_user (
    credentials: HTTPAuthorizationCredentials = Depends(security),
    conn: asyncpg.Connection = Depends(get_db_conn)
) -> object:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        account: str = payload.get("sub")
        if account is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await get_user_by_account(conn, account)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user
async def check_user_role(
    conn:asyncpg.Connection,
    group_id : int,
    user_id : int
    
):
    role = await get_user_role(conn,group_id,user_id)
    if not role:
        raise HTTPException(404,"This member is not in group")
    

