# app/schemas.py
from pydantic import BaseModel, EmailStr
from datetime import datetime

# -------- User --------
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    email: EmailStr
    username: str
    password: str

class UserRead(UserBase):
    id: int
    class Config:
        orm_mode = True

# -------- Post --------
class PostBase(BaseModel):
    content: str
    image_url: str | None = None   # <-- add optional image_url

class PostCreate(PostBase):
    pass

class PostRead(PostBase):
    id: int
    author_id: int
    created_at: datetime
    author: UserRead
    
    class Config:
        from_attributes = True

# --- Message ---
class MessageBase(BaseModel):
    content: str

class MessageCreate(MessageBase):
    receiver_id: int  # who to send the message to

class MessageRead(MessageBase):
    id: int
    sender_id: int
    receiver_id: int
    created_at: datetime
    sender_username: str  # Added sender username
    receiver_username: str  # Added receiver username

    class Config:
        from_attributes = True