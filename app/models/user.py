import email
from typing import Optional
from pydantic import BaseModel 
class UserCreate(BaseModel):
    account:str
    password : str
    full_name : str
class UserLogin(BaseModel):
    account:str
    password:str
class Token(BaseModel):
    access_token  : str
    token_type : str
class UserOut(BaseModel):
    user_id: int
    full_name: str
    account: str
    avatar_url: Optional[str] = None # <-- THÊM DÒNG NÀY