from typing import Literal
from pydantic import BaseModel, EmailStr
from datetime import datetime

# User management schema

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Post management schema

class PostBase(BaseModel):
    title: str
    content: str
    category: str = "Generic"
    published: bool = True

class PostCreate(PostBase):
    pass

class PostResponse(PostBase):
    id: int
    published: bool
    created_at: datetime
    user_id: int
    owner: UserResponse

    class Config:
        from_attributes = True

class PostWithVotes(BaseModel):
    Post: PostResponse
    vote_count: int

    class Config:
        from_attributes = True

# Login management schema

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    sub: str | None = None
    exp: datetime | None = None

# Voting management schema

class Vote(BaseModel):
    post_id: int
    dir: Literal[0, 1]