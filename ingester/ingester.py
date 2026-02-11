import asyncio
import os
import random
import uuid
from datetime import datetime, timezone
import redis.asyncio as redis

POSITIVE_TEMPLATES = [
    "I absolutely love {product}! Best purchase ever!",
    "Amazing experience with {product}, highly recommend!",
    "{product} exceeded all my expectations!",
    "So happy with {product}, works perfectly!",
    "Great quality {product}, worth every penny!",
    "{product} is fantastic! Customer service was excellent too.",
    "Just got {product} and I'm thrilled with it!",
    "Five stars for {product}! Outstanding product!",
    "Best {product} I've ever used, simply amazing!",
    "Love how {product} makes everything so easy!",
]

NEGATIVE_TEMPLATES = [
    "Very disappointed with {product}, total waste of money.",
    "Terrible experience with {product}, would not recommend.",
    "{product} broke after one week, horrible quality!",
    "Worst {product} ever, customer service was unhelpful.",
    "Stay away from {product}, complete disaster!",
    "{product} is a scam, doesn't work as advertised.",
    "Hate {product}, returning it immediately!",
    "Frustrated with {product}, nothing but problems.",
    "{product} is overpriced garbage, very disappointed.",
    "Never buying {product} again, awful experience!",
]

NEUTRAL_TEMPLATES = [
    "Just received {product} today, will test it out.",
    "Looking at reviews for {product} before deciding.",
    "{product} arrived on time, packaging was standard.",
    "Anyone else using {product}? Curious about opinions.",
    "Ordered {product} last week, waiting to see how it performs.",
    "{product} seems okay, nothing special so far.",
    "Comparing {product} with other options in the market.",
    "First time trying {product}, no strong opinion yet.",
    "The {product} works as described, meets basic needs.",
    "Thinking about getting {product}, need more info.",
]

PRODUCTS = [
    "iPhone 16", "Tesla Model 3", "ChatGPT", "Netflix", "Amazon Prime",
    "Spotify Premium", "MacBook Pro", "PlayStation 5", "Samsung Galaxy S24",
    "Google Pixel 9", "AirPods Pro", "Kindle Paperwhite", "Nintendo Switch",
    "Disney Plus", "Adobe Creative Cloud", "Microsoft 365",
]

SOURCES = ["reddit", "twitter", "facebook", "instagram", "tiktok"]

AUTHORS = [
    "tech_enthusiast", "daily_reviewer", "gadget_lover", "honest_user",
    "savvy_shopper", "product_tester", "real_consumer", "average_joe",
    "power_user", "casual_buyer", "deal_hunter", "quality_seeker",
]


class DataIngester:
    def __init__(self, redis_client, posts_per_minute: int = 10):
        self.redis_client = redis_client
        self.posts_per_minute = posts_per_minute
        self.stream_name = os.getenv("REDIS_STREAM_NAME", "social_posts_stream")
        self._running = False

    def generate_post(self) -> dict:
        sentiment_type = random.choices(
            ["positive", "neutral", "negative"],
            weights=[0.4, 0.3, 0.3]
        )[0]

        if sentiment_type == "positive":
            template = random.choice(POSITIVE_TEMPLATES)
        elif sentiment_type == "negative":
            template = random.choice(NEGATIVE_TEMPLATES)
        else:
            template = random.choice(NEUTRAL_TEMPLATES)

        product = random.choice(PRODUCTS)
        content = template.format(product=product)
        post_id = f"post_{uuid.uuid4().hex[:12]}"
        source = random.choice(SOURCES)
        author = random.choice(AUTHORS)
        created_at = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

        return {
            "post_id": post_id,
            "platform": source,
            "content": content,
            "author": author,
            "created_at": created_at,
        }

    async def publish_post(self, post: dict) -> bool:
        try:
            await self.redis_client.xadd(
                self.stream_name,
                {
                    "post_id": post["post_id"],
                    "platform": post["platform"],
                    "content": post["content"],
                    "author": post["author"],
                    "created_at": post["created_at"],
                }
            )
            return True
        except Exception as e:
            print(f"Error publishing post: {e}")
            return False

    async def start(self, duration_seconds: int = None):
        self._running = True
        delay = 60.0 / self.posts_per_minute
        posts_published = 0
        start_time = asyncio.get_running_loop().time()

        print(f"DataIngester started. Publishing {self.posts_per_minute} posts/minute to stream: {self.stream_name}")

        try:
            while self._running:
                if duration_seconds and (asyncio.get_running_loop().time() - start_time > duration_seconds):
                    print(f"Ingester reached duration limit of {duration_seconds}s.")
                    break

                post = self.generate_post()
                success = await self.publish_post(post)

                if success:
                    posts_published += 1
                    print(f"Published: {post['post_id']} | {post['platform']} | {post['content'][:50]}...")

                await asyncio.sleep(delay)

        except KeyboardInterrupt:
            print(f"\nIngester stopped. Published {posts_published} posts.")
        except Exception as e:
            print(f"Ingester error: {e}")
        finally:
            self._running = False
            print(f"Total posts published: {posts_published}")

    def stop(self):
        self._running = False


async def main():
    redis_host = os.getenv("REDIS_HOST", "redis")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    posts_per_minute = int(os.getenv("POSTS_PER_MINUTE", 60))

    print(f"Connecting to Redis at {redis_host}:{redis_port}...")

    redis_client = redis.Redis(
        host=redis_host,
        port=redis_port,
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

    ingester = DataIngester(
        redis_client=redis_client,
        posts_per_minute=posts_per_minute
    )

    await ingester.start()


if __name__ == "__main__":
    asyncio.run(main())
