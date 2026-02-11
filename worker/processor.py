from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.models import SocialMediaPost, SentimentAnalysis
from sentiment_analyzer import SentimentAnalyzer

analyzer = SentimentAnalyzer()


async def process_post(db: AsyncSession, post: dict):
    sentiment = analyzer.analyze(post["content"])

    db_post = SocialMediaPost(
        post_id=post["post_id"],
        source=post["source"],
        content=post["content"],
        created_at=datetime.utcnow()
    )

    db_sentiment = SentimentAnalysis(
        post_id=post["post_id"],
        sentiment_label=sentiment["label"],
        confidence_score=sentiment["confidence"],
        model_name="distilbert"
    )

    db.add(db_post)
    db.add(db_sentiment)
    await db.commit()
