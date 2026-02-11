from sqlalchemy import select, func
from backend.database import get_db
from backend.models import SocialMediaPost, SentimentAnalysis

async def get_realtime_metrics():
    async with async_session() as session:
        result = await session.execute(
            select(
                SentimentAnalysis.sentiment_label,
                func.count().label("count")
            ).group_by(SentimentAnalysis.sentiment_label)
        )

        sentiment = {"positive": 0, "negative": 0, "neutral": 0}

        for label, count in result.all():
            sentiment[label] = count

        return {
            "type": "realtime_update",
            "sentiment": sentiment,
            "total": sum(sentiment.values())
        }
