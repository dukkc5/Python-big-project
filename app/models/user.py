import email
from pydantic import BaseModel 
class UserCreate(BaseModel):
    acccount:str
    password : str
    full_name : str
class UserLogin(BaseModel):
    account:str
    password:str
class Token(BaseModel):
    access_token  : str
    token_type : str