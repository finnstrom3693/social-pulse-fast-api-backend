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

class PostCreate(PostBase):
    pass

class PostRead(PostBase):
    id: int
    author_id: int
    created_at: datetime
    author: UserRead
    
    class Config:
        from_attributes = True