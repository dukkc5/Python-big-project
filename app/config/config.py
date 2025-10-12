from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pathlib import Path
# config.py nằm ở: app/config/config.py
# → cần lên 3 cấp để đến gốc dự án
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # ← 3 lần .parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8"
    }

settings = Settings()