
# 🚀 FastAPI + Neon PostgreSQL Project

Một ứng dụng FastAPI kết nối database PostgreSQL trên [Neon.tech](https://neon.tech), được thiết kế để học tập và phát triển.

---

## 🔒 Cảnh báo bảo mật **(ĐỌC KỸ TRƯỚC KHI LÀM VIỆC)**

- **Tuyệt đối không commit file `.env` hoặc `config.py` chứa secret** (mật khẩu, token, URL có thông tin nhạy cảm).
- Nếu bạn **từng commit secret lên GitHub**:
  1. **Reset password trên Neon ngay lập tức**.
  2. **Tạo repo GitHub mới** để xóa lịch sử chứa secret.
  3. **Xóa repo cũ** trên GitHub.
- Một khi secret đã lên GitHub — **coi như đã bị lộ**. Luôn đổi secret sau khi dọn dẹp!

---

## 🛠️ Cách chạy dự án trên máy local

### 1. Clone repo
```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

### 2. Tạo virtual environment
```bash
# Windows (PowerShell)
python -m venv venv
venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Cài thư viện
```bash
pip install -r requirements.txt
```

### 4. Cấu hình biến môi trường
- Copy file mẫu:
  ```bash
  cp .env.example .env
  ```
- Mở `.env` và điền thông tin thật:
  ```env
  DATABASE_URL=postgresql://neondb_owner:your_new_password@your_host/neondb?sslmode=require
  SECRET_KEY=your_strong_secret_key_here
  ALGORITHM=HS256
  ACCESS_TOKEN_EXPIRE_MINUTES=60
  ```

> 💡 Tạo `SECRET_KEY` mạnh:
> ```python
> python -c "import secrets; print(secrets.token_urlsafe(32))"
> ```

### 5. Chạy ứng dụng
```bash
uvicorn app.main:app --reload
```
→ Truy cập: http://127.0.0.1:8000

---


## 🤝 Quy trình làm việc nhóm

1. Tạo branch mới:
   ```bash
   git checkout -b feature/your-feature
   ```
2. Commit thay đổi:
   ```bash
   git add .
   git commit -m "Add feature"
   ```
3. Push và tạo Pull Request:
   ```bash
   git push -u origin feature/your-feature
   ```

---
