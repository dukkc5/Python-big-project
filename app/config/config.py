from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()  # Đọc biến môi trường từ .env

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        env_file = ".env"  # Chỉ định file .env để đọc
        env_file_encoding = "utf-8"

settings = Settings()