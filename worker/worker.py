import sys
import os
import asyncio
from datetime import datetime, timezone
import redis.asyncio as redis

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import AsyncSessionLocal
from backend.models.models import SocialMediaPost, SentimentAnalysis
from backend.services.sentiment_analyzer import SentimentAnalyzer

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
STREAM_NAME = os.getenv("REDIS_STREAM_NAME", "social_posts_stream")
CONSUMER_GROUP = os.getenv("REDIS_CONSUMER_GROUP", "sentiment_workers")


class SentimentWorker:
    def __init__(self, redis_client, db_session_maker, stream_name: str = None, consumer_group: str = None):
        self.redis_client = redis_client
        self.db_session_maker = db_session_maker
        self.stream_name = stream_name or os.getenv("REDIS_STREAM_NAME", "social_posts_stream")
        self.consumer_group = consumer_group or os.getenv("REDIS_CONSUMER_GROUP", "sentiment_workers")
        self.consumer_name = f"worker-{os.getpid()}"
        self.analyzer = SentimentAnalyzer(model_type='local')
        self.messages_processed = 0
        self.errors = 0
        self.max_retries = 3

    async def _ensure_consumer_group(self):
        try:
            await self.redis_client.xgroup_create(
                self.stream_name,
                self.consumer_group,
                id="0",
                mkstream=True
            )
            print(f"Created consumer group: {self.consumer_group}")
        except Exception:
            pass

    async def process_message(self, message_id: str, message_data: dict) -> bool:
        retries = 0
        while retries < self.max_retries:
            try:
                post_id = message_data.get("post_id")
                content = message_data.get("content") or message_data.get("text")
                platform = message_data.get("platform") or message_data.get("source", "unknown")
                author = message_data.get("author", "anonymous")
                created_at_str = message_data.get("created_at")

                if not content or not post_id:
                    await self.redis_client.xack(self.stream_name, self.consumer_group, message_id)
                    return True


                sentiment_task = self.analyzer.analyze_sentiment(content)
                emotion_task = self.analyzer.analyze_emotion(content)
                
                sentiment_result, emotion_result = await asyncio.gather(sentiment_task, emotion_task)
                

                if not sentiment_result or not emotion_result:
                     raise ValueError("Analysis returned empty results")

                created_at = None
                if created_at_str:
                    try:
                        created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                    except Exception:
                        created_at = datetime.now(timezone.utc)

                async with self.db_session_maker() as session:
                    post = SocialMediaPost(
                        post_id=post_id,
                        platform=platform,
                        content=content,
                        author=author,
                        created_at=created_at,
                        ingested_at=datetime.now(timezone.utc)
                    )
                    session.add(post)

                    try:
                        await session.flush()
                    except Exception:
                        await session.rollback()
                        async with self.db_session_maker() as new_session:
                            analysis = SentimentAnalysis(
                                post_id=post_id,
                                model_name=sentiment_result["model_name"],
                                sentiment_label=sentiment_result["sentiment_label"],
                                confidence_score=sentiment_result["confidence_score"],
                                emotion=emotion_result["emotion"],
                                analyzed_at=datetime.now(timezone.utc)
                            )
                            new_session.add(analysis)
                            await new_session.commit()
                            await self.redis_client.xack(self.stream_name, self.consumer_group, message_id)
                            self.messages_processed += 1
                            return True

                    analysis = SentimentAnalysis(
                        post_id=post_id,
                        model_name=sentiment_result["model_name"],
                        sentiment_label=sentiment_result["sentiment_label"],
                        confidence_score=sentiment_result["confidence_score"],
                        emotion=emotion_result["emotion"],
                        analyzed_at=datetime.now(timezone.utc)
                    )
                    session.add(analysis)
                    await session.commit()

                await self.redis_client.xack(self.stream_name, self.consumer_group, message_id)
                self.messages_processed += 1

                print(f"Processed: {post_id} | {sentiment_result['sentiment_label']} ({sentiment_result['confidence_score']:.2f}) | {emotion_result['emotion']}")
                return True

            except Exception as e:
                retries += 1
                self.errors += 1
                print(f"Error processing message {message_id} (retry {retries}/{self.max_retries}): {e}")
                if retries >= self.max_retries:
                    await self.redis_client.xack(self.stream_name, self.consumer_group, message_id)
                    return False
                await asyncio.sleep(1)

        return False

    async def run(self, batch_size: int = 10, block_ms: int = 5000):
        await self._ensure_consumer_group()
        print(f"SentimentWorker {self.consumer_name} started. Waiting for messages from {self.stream_name}...")

        while True:
            try:
                messages = await self.redis_client.xreadgroup(
                    self.consumer_group,
                    self.consumer_name,
                    streams={self.stream_name: ">"},
                    count=batch_size,
                    block=block_ms
                )

                if not messages:
                    continue

                tasks = []
                for stream_name, entries in messages:
                    for message_id, message_data in entries:
                        tasks.append(self.process_message(message_id, message_data))

                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)

                if self.messages_processed > 0 and self.messages_processed % 10 == 0:
                    print(f"Stats: processed={self.messages_processed}, errors={self.errors}")

            except Exception as e:
                print(f"Worker loop error: {e}")
                await asyncio.sleep(5)


async def main():
    print("SentimentWorker starting...")
    print("Loading ML models...")

    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True
    )

    while True:
        try:
            await redis_client.ping()
            print("Redis connection established.")
            break
        except Exception as e:
            print(f"Redis connection failed: {e}. Retrying in 5s...")
            await asyncio.sleep(5)

    worker = SentimentWorker(
        redis_client=redis_client,
        db_session_maker=AsyncSessionLocal,
        stream_name=STREAM_NAME,
        consumer_group=CONSUMER_GROUP
    )

    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
