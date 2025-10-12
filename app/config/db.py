from contextlib import asynccontextmanager
from fastapi import FastAPI
import asyncpg
from app.config.config import settings

_pool = None

async def init_db_pool():
    global _pool
    _pool = await asyncpg.create_pool(
        dsn=settings.DATABASE_URL,
        min_size=2,
        max_size=10,
        command_timeout=60,
        statement_cache_size=0
    )

async def close_db_pool():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None

@asynccontextmanager
async def get_db():
    if _pool is None:
        raise RuntimeError("DB pool not initialized")
    async with _pool.acquire() as conn:
        yield conn

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db_pool()
    yield
    await close_db_pool()