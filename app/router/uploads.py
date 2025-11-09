import os
from pathlib import Path
import shutil
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
import asyncpg
from fastapi.responses import FileResponse

from app.api.deps import get_db_conn, get_current_user
# (QUAN TRỌNG) Import hàm CRUD mới
from app.api.crud.task_assignment_crud import update_assignment_file

router = APIRouter(
    prefix="/files",
    tags=["Files"],
)

# Đường dẫn thư mục để lưu file
from pathlib import Path

UPLOAD_DIRECTORY = Path("./upload").resolve()


# Đảm bảo thư mục tồn tại
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

@router.post("/uploads", status_code=status.HTTP_200_OK)
async def upload_file(
    assignment_id: int = Form(...),
    file: UploadFile = File(...),
    conn: asyncpg.Connection = Depends(get_db_conn),
    current_user: dict = Depends(get_current_user)
):
    
    try:
        # Tạo tên file duy nhất để tránh ghi đè
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_location = os.path.join(UPLOAD_DIRECTORY, unique_filename)

        # Lưu file vào thư mục
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)

        file_url = f"/uploads/{unique_filename}"
        
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
@router.get("/{filename}")
def get_file(filename: str):
    file_path = f"upload/{filename}"
    return FileResponse(file_path)
@router.delete("/{assignment_id}", status_code=status.HTTP_200_OK)
async def remove_file_by_assignment(
    assignment_id: int,
    conn: asyncpg.Connection = Depends(get_db_conn),
    current_user: dict = Depends(get_current_user)
):
    
    record = await conn.fetchrow(
        "SELECT attachment_url FROM task_assignments WHERE assignment_id = $1",
        assignment_id
    )
    if not record or not record.get("attachment_url"):
        raise HTTPException(status_code=404, detail="Không tìm thấy file để xóa")

    file_url = record["attachment_url"]  
    filename = Path(file_url).name
    target = (UPLOAD_DIRECTORY / filename).resolve()

    if not str(target).startswith(str(UPLOAD_DIRECTORY)):
        raise HTTPException(status_code=400, detail="File path không hợp lệ")

    try:
        if target.exists():
            target.unlink()
        # cập nhật DB: xóa đường dẫn file (sử dụng hàm CRUD đã có)
        await update_assignment_file(conn, assignment_id, None)
        return {"message": "Đã xóa file và cập nhật DB", "assignment_id": assignment_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi xóa file: {e}")

