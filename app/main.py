from fastapi import FastAPI
from websockets import route

from app.config.db import lifespan
from app.router import auth, groups

app = FastAPI(
    title="TeamWork Env",
    description="API for managing group and assigning tasks",
    lifespan=lifespan
)
app.include_router(auth.router)
app.include_router(groups.router)
@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Bay h la 1h56"}
print("hello worldđd")