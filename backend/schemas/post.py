from pydantic import BaseModel

class PostCreate(BaseModel):
    content: str
    platform: str
    author: str
