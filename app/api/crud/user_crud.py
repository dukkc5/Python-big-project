import asyncpg
from app.config import security

async def create_user(conn: asyncpg.Connection, email: str, password: str, full_name: str):
    hash_pw = security.hash_password(password)  # Hash bằng argon2
    await conn.execute(
        "INSERT INTO users (email, password_hash, full_name) VALUES ($1, $2, $3)",
        email, hash_pw, full_name
    )
async def get_user_by_email(conn: asyncpg.Connection, email: str):
    row = await conn.fetchrow("SELECT * FROM users WHERE email = $1", email)
    return dict(row) if row else None
async def get_user_by_id(conn: asyncpg.Connection, id: int):
    row = await conn.fetchrow("SELECT * FROM users WHERE id = $1", id)
    return dict(row) if row else None