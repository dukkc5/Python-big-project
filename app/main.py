import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from websockets import route

from app.config.db import lifespan
from app.router import auth, chat, group_invitations, groups, notifications, task_assignment, tasks_groups, uploads

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
# (MỚI) Tạo thư mục 'static' nếu chưa có
os.makedirs("static/avatars/users", exist_ok=True) 
os.makedirs("static/avatars/groups", exist_ok=True)

# (MỚI) Mount thư mục static
# Giờ đây, file tại 'static/avatars/my_image.png'
# Sẽ có thể truy cập qua URL: 'http://your_domain.com/static/avatars/my_image.png'
app.mount("/static", StaticFiles(directory="static"), name="static")

# ... (Thêm các router của bạn)
# app.include_router(user_router)
# app.include_router(group_router)
app.include_router(auth.router)
app.include_router(groups.router)
app.include_router(tasks_groups.router)
app.include_router(group_invitations.router)
app.include_router(task_assignment.router)
app.include_router(uploads.router)
app.include_router(chat.router)
app.include_router(notifications.router)
@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Bay h la 1h56"}
print("hello worldđd")