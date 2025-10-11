from passlib.context import CryptContext
from app.config.config import settings
from jose import JWTError , jwt
from datetime import datetime, timedelta
# Tạo context hash password
pwd_context = CryptContext(
    schemes=["argon2"],   # Sử dụng argon2 thay cho bcrypt
    deprecated="auto"
)

# Hash mật khẩu
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Kiểm tra mật khẩu
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
def create_acess_token(data : dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=settings.ACESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    token = jwt.encode(to_encode,settings.SECRET_KEY,settings.ALGORITHM)
    return token


