from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PostBase(BaseModel):
    content: str
    platform: Optional[str] = "web"
    author: Optional[str] = "anonymous"

class PostCreate(PostBase):
    pass

class SentimentResponse(BaseModel):
    id: int
    post_id: int
    sentiment: str
    score: float
    emotion: Optional[str] = None
    processed_at: datetime

    class Config:
        orm_mode = True

class PostResponse(PostBase):
    id: int
    created_at: datetime
    sentiment: Optional[SentimentResponse] = None

    class Config:
        orm_mode = True
