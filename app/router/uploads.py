import os
import shutil
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
import asyncpg

from app.api.deps import get_db_conn, get_current_user
# (QUAN TRỌNG) Import hàm CRUD mới
from app.api.crud.task_assignment_crud import update_assignment_file

router = APIRouter(
    prefix="/files",
    tags=["Files"],
)

# Đường dẫn thư mục để lưu file
UPLOAD_DIRECTORY = "./uploads"

# Đảm bảo thư mục tồn tại
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

@router.post("/upload", status_code=status.HTTP_200_OK)
async def upload_file(
    assignment_id: int = Form(...),
    file: UploadFile = File(...),
    conn: asyncpg.Connection = Depends(get_db_conn),
    current_user: dict = Depends(get_current_user)
):
    """
    Nhận file upload (multipart/form-data) và một assignment_id.
    Lưu file vào thư mục /uploads và cập nhật đường dẫn vào CSDL.
    """
    try:
        # Tạo tên file duy nhất để tránh ghi đè
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_location = os.path.join(UPLOAD_DIRECTORY, unique_filename)

        # Lưu file vào thư mục
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)

        # Tạo URL (đường dẫn) mà frontend có thể truy cập
        # (Vì chúng ta sẽ mount /uploads ở main.py)
        file_url = f"/uploads/{unique_filename}"
        
        # Cập nhật CSDL
        await update_assignment_file(conn, assignment_id, file_url)

        return {"file_url": file_url, "assignment_id": assignment_id}

    except Exception as e:
        # Xử lý nếu có lỗi
        print(f"Lỗi upload file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể upload file: {e}",
        )
    finally:
        # Luôn đóng file
        file.file.close()

