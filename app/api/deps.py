import asyncpg
from fastapi import Depends
from fastapi import security,HTTPException
from app.config.db import get_db
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from jose import JWTError , jwt
from app.api.crud.user_crud import get_user_by_email
security =  HTTPBearer()
from app.config.config import settings

async def get_db_conn():
    async with get_db() as conn:
        yield conn
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    conn: asyncpg.Connection = Depends(get_db_conn)
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await get_user_by_email(conn, email)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

