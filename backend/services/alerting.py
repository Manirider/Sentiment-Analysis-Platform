import os
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import AsyncSessionLocal
from backend.models.models import SentimentAnalysis, SentimentAlert


class AlertService:
    def __init__(self, db_session_maker, redis_client=None):
        self.db_session_maker = db_session_maker
        self.redis_client = redis_client
        self.threshold = float(os.getenv("ALERT_NEGATIVE_RATIO_THRESHOLD", "2.0"))
        self.window_minutes = int(os.getenv("ALERT_WINDOW_MINUTES", "5"))
        self.min_posts = int(os.getenv("ALERT_MIN_POSTS", "10"))
        self._running = False

    async def check_thresholds(self) -> Optional[dict]:
        async with self.db_session_maker() as session:
            window_end = datetime.now(timezone.utc)
            window_start = window_end - timedelta(minutes=self.window_minutes)

            result = await session.execute(
                select(
                    SentimentAnalysis.sentiment_label,
                    func.count().label("count")
                )
                .where(SentimentAnalysis.analyzed_at >= window_start)
                .where(SentimentAnalysis.analyzed_at <= window_end)
                .group_by(SentimentAnalysis.sentiment_label)
            )

            counts = {"positive": 0, "negative": 0, "neutral": 0}
            for label, count in result.all():
                if label in counts:
                    counts[label] = count

            total = sum(counts.values())

            if total < self.min_posts:
                return None

            positive_count = counts["positive"]
            negative_count = counts["negative"]

            if positive_count == 0:
                ratio = float(negative_count) if negative_count > 0 else 0.0
            else:
                ratio = negative_count / positive_count

            if ratio > self.threshold:
                return {
                    "alert_triggered": True,
                    "alert_type": "high_negative_ratio",
                    "threshold": self.threshold,
                    "actual_ratio": round(ratio, 2),
                    "window_minutes": self.window_minutes,
                    "window_start": window_start.isoformat(),
                    "window_end": window_end.isoformat(),
                    "metrics": {
                        "positive_count": positive_count,
                        "negative_count": negative_count,
                        "neutral_count": counts["neutral"],
                        "total_count": total
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }

            return None

    async def save_alert(self, alert_data: dict) -> int:
        async with self.db_session_maker() as session:
            alert = SentimentAlert(
                alert_type=alert_data["alert_type"],
                threshold_value=alert_data["threshold"],
                actual_value=alert_data["actual_ratio"],
                window_start=datetime.fromisoformat(alert_data["window_start"]),
                window_end=datetime.fromisoformat(alert_data["window_end"]),
                post_count=alert_data["metrics"]["total_count"],
                triggered_at=datetime.now(timezone.utc),
                details=alert_data["metrics"]
            )
            session.add(alert)
            await session.commit()
            await session.refresh(alert)
            return alert.id

    async def run_monitoring_loop(self, check_interval_seconds: int = 60):
        self._running = True
        print(f"Alert monitoring started. Checking every {check_interval_seconds}s...")

        while self._running:
            try:
                alert_data = await self.check_thresholds()

                if alert_data:
                    alert_id = await self.save_alert(alert_data)
                    print(f"ALERT TRIGGERED! ID={alert_id} | Ratio={alert_data['actual_ratio']} > {alert_data['threshold']}")

            except Exception as e:
                print(f"Alert monitoring error: {e}")

            await asyncio.sleep(check_interval_seconds)

    def stop(self):
        self._running = False
