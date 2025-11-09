# Import các thư viện cần thiết
import os
import shutil
import uuid
from fastapi import APIRouter, Body, Depends, File, HTTPException, UploadFile, status
import asyncpg
import logging # Thêm thư viện logging để ghi lại lỗi

# Import các exception cụ thể từ asyncpg
from asyncpg.exceptions import UniqueViolationError, DataError
from h11 import Connection

from app.api.crud.user_crud import create_user, get_user_by_account, update_fcm_token
from app.api.deps import get_current_user, get_db_conn
from app.models import user 
from app.config.security import verify_password, create_acess_token

# Khởi tạo router
router = APIRouter(prefix="/auth", tags=["auth"])
STATIC_AVATAR_DIR = "static/avatars/users"
BASE_URL = "https://oared-willa-teughly.ngrok-free.dev" # (URL ngrok của bạn)

@router.post("/me/avatar")
async def upload_user_avatar(
    current_user=Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db_conn),
    file: UploadFile = File(...)
):
    """Tải lên avatar cho user hiện tại."""
    
    # 1. Kiểm tra loại file (tùy chọn nhưng nên có)

    # 2. Tạo tên file duy nhất
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(STATIC_AVATAR_DIR, unique_filename)

    # 3. Lưu file vào thư mục static
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Không thể lưu file: {e}")
    finally:
        file.file.close()

    # 4. Tạo URL đầy đủ
    # (Quan trọng: URL này phải khớp với cách bạn 'mount' StaticFiles)
    avatar_url = f"{BASE_URL}/static/avatars/users/{unique_filename}"

    # 5. Cập nhật CSDL
    await conn.execute(
        "UPDATE users SET avatar_url = $1 WHERE user_id = $2",
        avatar_url, current_user["user_id"]
    )

    return {"avatar_url": avatar_url}
@router.get("/me",response_model=user.UserOut)
async def get_me(current_user = Depends(get_current_user)):
    return current_user
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user: user.UserCreate, 
    conn: asyncpg.Connection = Depends(get_db_conn)
):
   
    try:
        db_user = await get_user_by_account(conn, user.account)
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account đã được đăng ký"
            )

        await create_user(conn, user.account, user.password, user.full_name)
        
        return {"msg": "User created"}
    except UniqueViolationError:
        # Lỗi 409 (Conflict) khi 2 người đăng ký cùng lúc (race condition)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Account này vừa được đăng ký. Vui lòng thử lại."
        )
    except DataError as e:
        # Lỗi 422 (Unprocessable Entity) khi dữ liệu gửi lên không hợp lệ 
        # (ví dụ: tên quá dài so với cột CSDL)
        logging.warning(f"Lỗi DataError khi đăng ký: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Dữ liệu không hợp lệ. {e}"
        )
        
    # --- 4. Bắt tất cả các lỗi hệ thống còn lại ---
    except Exception as e:
        # Ghi lại lỗi 500 ra log để lập trình viên sửa
        logging.error(f"Lỗi hệ thống 500 khi /register: {e}", exc_info=True)
        # Trả về lỗi 500 chung chung
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Có lỗi hệ thống xảy ra. Vui lòng thử lại sau."
        )


@router.post("/login")
async def login(
    user: user.UserLogin, 
    conn: asyncpg.Connection = Depends(get_db_conn)
):
    """
    Endpoint để đăng nhập và trả về token.
    Đã được bọc try-except để xử lý lỗi CSDL.
    """
    try:
        # --- 1. Thực thi I/O (Đọc CSDL) ---
        db_user = await get_user_by_account(conn, user.account)

        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tài khoản hoặc mật khẩu không chính xác"
            )
            
        if not verify_password(user.password, db_user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tài khoản hoặc mật khẩu không chính xác"
            )
        access_token = create_acess_token(data={"sub": db_user["account"]})
        
        return {"access_token": access_token, "token_type": "bearer"}

    except Exception as e:
        # Lỗi này có thể xảy ra nếu CSDL mất kết nối khi đang 'get_user_by_email'
        logging.error(f"Lỗi hệ thống 500 khi /login: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Có lỗi hệ thống xảy ra. Vui lòng thử lại sau."
        )
@router.post("/register-device", status_code=status.HTTP_200_OK)
async def register_device_token(
    fcm_token: str = Body(..., embed=True), # Nhận token từ body
    conn: asyncpg.Connection = Depends(get_db_conn),
    current_user: dict = Depends(get_current_user) # Yêu cầu user phải đăng nhập
):
    """
    Nhận FCM token từ thiết bị (Flutter) và lưu vào CSDL
    cho user đang đăng nhập.
    """
    user_id = current_user["user_id"]
    try:
        # (Chúng ta sẽ thêm hàm này vào user_crud ở bước sau)
        await update_fcm_token(conn, user_id, fcm_token)
        return {"message": "Cập nhật FCM token thành công"}
    except Exception as e:
        print(f"Lỗi cập nhật FCM token: {e}")
        raise HTTPException(status_code=500, detail="Lỗi server khi cập nhật token")