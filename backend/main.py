import os
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Optional, List
import redis.asyncio as redis
from fastapi import FastAPI, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import engine, Base, AsyncSessionLocal
from backend.models.models import SocialMediaPost, SentimentAnalysis, SentimentAlert
from backend.services.alerting import AlertService

app = FastAPI(title="Sentiment Analysis API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
redis_client = None

connected_websockets: List[WebSocket] = []


@app.on_event("startup")
async def startup():
    global redis_client
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    print("Database tables created. Redis connected.")


    alert_service = AlertService(db_session_maker=AsyncSessionLocal, redis_client=redis_client)
    asyncio.create_task(alert_service.run_monitoring_loop())


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@app.get("/api/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    db_status = "disconnected"
    redis_status = "disconnected"
    total_posts = 0
    total_analyses = 0
    recent_posts_1h = 0

    try:
        await db.execute(select(func.count()).select_from(SocialMediaPost))
        db_status = "connected"
    except Exception:
        pass

    try:
        if redis_client:
            await redis_client.ping()
            redis_status = "connected"
    except Exception:
        pass

    try:
        result = await db.execute(select(func.count()).select_from(SocialMediaPost))
        total_posts = result.scalar() or 0

        result = await db.execute(select(func.count()).select_from(SentimentAnalysis))
        total_analyses = result.scalar() or 0

        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
        result = await db.execute(
            select(func.count()).select_from(SocialMediaPost)
            .where(SocialMediaPost.ingested_at >= one_hour_ago)
        )
        recent_posts_1h = result.scalar() or 0
    except Exception:
        pass

    return {
        "status": "healthy" if db_status == "connected" and redis_status == "connected" else "degraded",
        "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        "services": {
            "database": db_status,
            "redis": redis_status
        },
        "stats": {
            "total_posts": total_posts,
            "total_analyses": total_analyses,
            "recent_posts_1h": recent_posts_1h
        }
    }


@app.get("/api/posts")
async def get_posts(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    platform: Optional[str] = Query(None),
    sentiment: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    query = (
        select(SocialMediaPost, SentimentAnalysis)
        .outerjoin(SentimentAnalysis, SocialMediaPost.post_id == SentimentAnalysis.post_id)
    )

    if platform:
        query = query.where(SocialMediaPost.platform == platform)
    if sentiment:
        query = query.where(SentimentAnalysis.sentiment_label == sentiment)

    count_query = select(func.count()).select_from(SocialMediaPost)
    if platform:
        count_query = count_query.where(SocialMediaPost.platform == platform)
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(SocialMediaPost.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    rows = result.all()

    posts = []
    for post, analysis in rows:
        post_data = {
            "post_id": post.post_id,
            "platform": post.platform,
            "content": post.content,
            "author": post.author,
            "created_at": post.created_at.isoformat().replace('+00:00', 'Z') if post.created_at else None,
            "sentiment": None
        }
        if analysis:
            post_data["sentiment"] = {
                "label": analysis.sentiment_label,
                "confidence": analysis.confidence_score,
                "emotion": analysis.emotion,
                "model_name": analysis.model_name
            }
        posts.append(post_data)

    return {
        "posts": posts,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@app.get("/api/analytics")
async def get_analytics(
    hours: int = Query(24, ge=1, le=168),
    platform: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    threshold = datetime.now(timezone.utc) - timedelta(hours=hours)

    query = select(
        SentimentAnalysis.sentiment_label,
        func.count().label("count")
    ).where(SentimentAnalysis.analyzed_at >= threshold)

    if platform:
        query = query.join(SocialMediaPost, SocialMediaPost.post_id == SentimentAnalysis.post_id)
        query = query.where(SocialMediaPost.platform == platform)

    query = query.group_by(SentimentAnalysis.sentiment_label)
    result = await db.execute(query)

    counts = {"positive": 0, "negative": 0, "neutral": 0}
    for label, count in result.all():
        if label in counts:
            counts[label] = count

    positive_count = counts["positive"]
    negative_count = counts["negative"]
    neutral_count = counts["neutral"]
    total_count = positive_count + negative_count + neutral_count

    percentages = {
        "positive": round((positive_count / total_count * 100), 2) if total_count > 0 else 0,
        "negative": round((negative_count / total_count * 100), 2) if total_count > 0 else 0,
        "neutral": round((neutral_count / total_count * 100), 2) if total_count > 0 else 0
    }

    distribution = [
        {"label": "positive", "count": positive_count, "percentage": percentages["positive"]},
        {"label": "negative", "count": negative_count, "percentage": percentages["negative"]},
        {"label": "neutral", "count": neutral_count, "percentage": percentages["neutral"]},
    ]

    return {
        "timeframe_hours": hours,
        "positive_count": positive_count,
        "negative_count": negative_count,
        "neutral_count": neutral_count,
        "total_count": total_count,
        "percentages": percentages,
        "distribution": distribution
    }


@app.websocket("/ws/sentiment")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_websockets.append(websocket)

    await websocket.send_json({
        "type": "connected",
        "message": "Connected to sentiment stream",
        "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    })

    last_metrics_time = asyncio.get_event_loop().time()

    try:
        while True:
            current_time = asyncio.get_event_loop().time()

            if current_time - last_metrics_time >= 30:
                async with AsyncSessionLocal() as db:
                    now = datetime.now(timezone.utc)

                    async def get_counts(since: datetime):
                        result = await db.execute(
                            select(
                                SentimentAnalysis.sentiment_label,
                                func.count().label("count")
                            ).where(SentimentAnalysis.analyzed_at >= since)
                            .group_by(SentimentAnalysis.sentiment_label)
                        )
                        counts = {"positive": 0, "negative": 0, "neutral": 0, "total": 0}
                        for label, count in result.all():
                            if label in counts:
                                counts[label] = count
                        counts["total"] = counts["positive"] + counts["negative"] + counts["neutral"]
                        return counts

                    metrics = {
                        "type": "metrics_update",
                        "data": {
                            "last_minute": await get_counts(now - timedelta(minutes=1)),
                            "last_hour": await get_counts(now - timedelta(hours=1)),
                            "last_24_hours": await get_counts(now - timedelta(hours=24))
                        },
                        "timestamp": now.isoformat().replace('+00:00', 'Z')
                    }

                await websocket.send_json(metrics)
                last_metrics_time = current_time

            try:
                await asyncio.wait_for(websocket.receive_text(), timeout=1.0)
            except asyncio.TimeoutError:
                pass

    except WebSocketDisconnect:
        pass
    finally:
        if websocket in connected_websockets:
            connected_websockets.remove(websocket)


async def broadcast_new_post(post_data: dict):
    message = {
        "type": "new_post",
        "data": {
            "post_id": post_data.get("post_id"),
            "content": post_data.get("content", "")[:100],
            "platform": post_data.get("platform"),
            "sentiment_label": post_data.get("sentiment_label"),
            "confidence_score": post_data.get("confidence_score"),
            "emotion": post_data.get("emotion"),
            "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        }
    }

    for ws in connected_websockets[:]:
        try:
            await ws.send_json(message)
        except Exception:
            if ws in connected_websockets:
                connected_websockets.remove(ws)


async def broadcast_metrics(metrics: dict):
    message = {
        "type": "metrics_update",
        "data": metrics,
        "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    }

    for ws in connected_websockets[:]:
        try:
            await ws.send_json(message)
        except Exception:
            if ws in connected_websockets:
                connected_websockets.remove(ws)
