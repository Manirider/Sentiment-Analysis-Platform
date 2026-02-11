from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, JSON
from sqlalchemy.sql import func
from backend.database import Base


class SocialMediaPost(Base):
    __tablename__ = "social_media_posts"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(String(255), unique=True, nullable=False, index=True)
    platform = Column(String(50), index=True, default="web")
    content = Column(Text, nullable=False)
    author = Column(String(255), default="anonymous")
    created_at = Column(DateTime(timezone=True), nullable=True, index=True)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class SentimentAnalysis(Base):
    __tablename__ = "sentiment_analysis"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(String(255), ForeignKey("social_media_posts.post_id", ondelete="CASCADE"), nullable=False, index=True)
    model_name = Column(String(100), nullable=False)
    sentiment_label = Column(String(20), nullable=False, index=True)
    confidence_score = Column(Float, nullable=False)
    emotion = Column(String(50), nullable=True)
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class SentimentAlert(Base):
    __tablename__ = "sentiment_alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String(50), nullable=False)
    threshold_value = Column(Float, nullable=False)
    actual_value = Column(Float, nullable=False)
    window_start = Column(DateTime(timezone=True), nullable=False)
    window_end = Column(DateTime(timezone=True), nullable=False)
    post_count = Column(Integer, nullable=False)
    triggered_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    details = Column(JSON, nullable=True)
