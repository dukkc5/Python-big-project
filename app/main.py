from fastapi import FastAPI
from websockets import route

from app.config.db import lifespan
from app.router import auth, group_invitations, groups, notifications, task_assignment, tasks_groups, uploads

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
app.include_router(tasks_groups.router)
app.include_router(group_invitations.router)
app.include_router(task_assignment.router)
app.include_router(notifications.router)
app.include_router(uploads.router)
@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Bay h la 1h56"}
print("hello worldđd")