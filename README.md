
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
git clone https://github.com/dukkc5/Python-big-project.git
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
## 🔄 Luồng làm việc với Git (Git Workflow)

Để đảm bảo **mã nguồn sạch, dễ quản lý và tránh xung đột**, hãy tuân theo luồng làm việc sau:

### 1. **Bắt đầu từ `main` luôn cập nhật mới nhất**
```bash
git checkout main
git pull origin main
```

### 2. **Tạo branch riêng cho từng tính năng hoặc sửa lỗi**
- Tên branch nên mô tả rõ ràng:
  - ✅ `feature/user-login`
  - ✅ `fix/db-connection-timeout`
  - ✅ `docs/update-readme`
- Tạo và chuyển sang branch:
  ```bash
  git checkout -b feature/your-feature
  ```

### 3. **Làm việc và commit thường xuyên**
- Mỗi commit nên:
  - Có **mô tả ngắn gọn, rõ ràng**.
  - Chỉ chứa **một thay đổi logic**.
- Ví dụ:
  ```bash
  git add .
  git commit -m "Add user authentication with JWT"
  ```

### 4. **Đồng bộ với `main` trước khi push**
Nếu `main` có thay đổi mới:
```bash
git checkout main
git pull origin main
git checkout feature/your-feature
git rebase main          # hoặc git merge main
```

### 5. **Push branch lên GitHub và tạo Pull Request (PR)**
```bash
git push -u origin feature/your-feature
```
→ Vào GitHub → tạo **Pull Request** vào `main`.

### 6. **Sau khi PR được duyệt:**
- **Merge vào `main`** (ưu tiên "Squash and merge" để giữ lịch sử gọn).
- **Xóa branch local và remote**:
  ```bash
  git checkout main
  git pull origin main
  git branch -d feature/your-feature          # xóa local
  git push origin --delete feature/your-feature  # xóa remote
  ```

---

## ⚠️ Lưu ý quan trọng khi làm việc với Git

| Vấn đề | Cách tránh |
|-------|-----------|
| **Commit secret** | Luôn kiểm tra `.gitignore`. Dùng `.env.example` thay vì `.env`. |
| **Làm trực tiếp trên `main`** | Không bao giờ! Luôn tạo branch mới. |
| **Force push (`--force`)** | Tránh dùng nếu làm việc nhóm. Chỉ dùng trên branch cá nhân. |
| **Commit quá lớn** | Chia nhỏ thành nhiều commit có ý nghĩa. |
| **Không pull trước khi push** | Luôn `git pull` hoặc `git fetch` trước khi push để tránh xung đột. |
| **Tên commit mơ hồ** | Viết commit message rõ ràng: *"Fix login bug"* thay vì *"update code"*. |

---

## 🔐 Mẹo bảo mật Git

- **Không bao giờ** commit:
  - File `.env`, `config.py` có secret
  - File log, file tạm, IDE config (`.vscode/`, `.idea/`)
- **Luôn có `.gitignore`** phù hợp với ngôn ngữ (Python, Node.js, v.v.).
- Nếu lỡ commit secret:
  1. **Đổi secret ngay** (Neon, API key, v.v.).
  2. **Xóa lịch sử Git** bằng `git filter-repo`.
  3. **Tốt nhất: tạo repo mới** và xóa repo cũ.

---
