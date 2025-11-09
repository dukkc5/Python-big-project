import asyncpg
from app.config import security

async def create_user(conn: asyncpg.Connection, account: str, password: str, full_name: str):
    hash_pw = security.hash_password(password)  # Hash bằng argon2
    await conn.execute(
        "INSERT INTO users (account, password_hash, full_name) VALUES ($1, $2, $3)",
        account, hash_pw, full_name
    )
async def get_user_by_account(conn: asyncpg.Connection, account:str):
    row = await conn.fetchrow("SELECT * FROM users WHERE account = $1", account) # sửa email thành account
    return dict(row) if row else None
async def get_user_by_id(conn: asyncpg.Connection, id: int):
    row = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", id)
    return dict(row) if row else None
async def update_fcm_token(conn: asyncpg.Connection, user_id: int, fcm_token: str):
    """
    Cập nhật hoặc chèn fcm_token cho một user.
    """
    query = """
        UPDATE users
        SET fcm_token = $1
        WHERE user_id = $2
    """
    await conn.execute(query, fcm_token, user_id)

# (MỚI) Hàm này sẽ cần ở bước sau
async def get_fcm_token(conn: asyncpg.Connection, user_id: int) -> str | None:
    """
    Lấy fcm_token của một user.
    """
    return await conn.fetchval("SELECT fcm_token FROM users WHERE user_id = $1", user_id)