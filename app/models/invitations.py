from pydantic import BaseModel

class Invitations(BaseModel):
    title:str
    group_id:int
    sender_id :int
    recipient_id :int
    status : str 
