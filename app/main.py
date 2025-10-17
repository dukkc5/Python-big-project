from fastapi import FastAPI
from websockets import route

from app.config.db import lifespan
from app.router import auth, groups, tasks

app = FastAPI(
    title="TeamWork Env",
    description="API for managing group and assigning tasks",
    lifespan=lifespan
)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ← cho phép tất cả domain (chỉ dùng trong dev!)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router)
app.include_router(groups.router)
app.include_router(tasks.router)
@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Bay h la 1h56"}
print("hello worldđd")