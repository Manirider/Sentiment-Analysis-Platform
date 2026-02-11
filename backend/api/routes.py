from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.database import get_db
from backend.models.models import SocialMediaPost

router = APIRouter(prefix="/api")

@router.get("/posts")
async def get_posts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SocialMediaPost))
    posts = result.scalars().all()
    return posts
