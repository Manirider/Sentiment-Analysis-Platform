import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MockRedis:
    def __init__(self):
        self.streams = {}
        self.groups = {}

    async def ping(self):
        return True

    async def xadd(self, stream, data):
        if stream not in self.streams:
            self.streams[stream] = []
        msg_id = f"{len(self.streams[stream])}-0"
        self.streams[stream].append((msg_id, data))
        return msg_id

    async def xgroup_create(self, stream, group, id="0", mkstream=False):
        self.groups[group] = {"stream": stream, "id": id}

    async def xreadgroup(self, group, consumer, streams, count=1, block=0):
        stream_name = list(streams.keys())[0]
        if stream_name in self.streams and self.streams[stream_name]:
            msg = self.streams[stream_name].pop(0)
            return [(stream_name, [msg])]
        return []

    async def xack(self, stream, group, msg_id):
        return 1


class MockDBSession:
    def __init__(self):
        self.items = []
        self.committed = False

    def add(self, item):
        self.items.append(item)

    async def commit(self):
        self.committed = True

    async def rollback(self):
        self.items = []

    async def flush(self):
        pass

    async def refresh(self, item):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass


@pytest.mark.asyncio
async def test_data_ingester_class_exists():
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "ingester"))
    from ingester import DataIngester
    assert DataIngester is not None


@pytest.mark.asyncio
async def test_data_ingester_init():
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "ingester"))
    from ingester import DataIngester

    mock_redis = MockRedis()
    ingester = DataIngester(mock_redis, posts_per_minute=10)

    assert ingester.redis_client == mock_redis
    assert ingester.posts_per_minute == 10


@pytest.mark.asyncio
async def test_data_ingester_generate_post_structure():
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "ingester"))
    from ingester import DataIngester

    ingester = DataIngester(MockRedis(), posts_per_minute=10)
    post = ingester.generate_post()

    assert "post_id" in post
    assert "platform" in post
    assert "content" in post
    assert "author" in post
    assert "created_at" in post


@pytest.mark.asyncio
async def test_data_ingester_generate_post_content_length():
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "ingester"))
    from ingester import DataIngester

    ingester = DataIngester(MockRedis(), posts_per_minute=10)
    post = ingester.generate_post()

    assert len(post["content"]) >= 20
    assert len(post["content"]) <= 500


@pytest.mark.asyncio
async def test_data_ingester_publish_post():
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "ingester"))
    from ingester import DataIngester

    mock_redis = MockRedis()
    ingester = DataIngester(mock_redis, posts_per_minute=10)
    post = ingester.generate_post()
    result = await ingester.publish_post(post)

    assert result is True
    assert ingester.stream_name in mock_redis.streams
    assert len(mock_redis.streams[ingester.stream_name]) == 1


@pytest.mark.asyncio
async def test_sentiment_worker_class_exists():
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "worker"))
    from worker import SentimentWorker
    assert SentimentWorker is not None


@pytest.mark.asyncio
async def test_sentiment_worker_has_process_message():
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "worker"))
    from worker import SentimentWorker

    mock_redis = MockRedis()
    worker = SentimentWorker(
        redis_client=mock_redis,
        db_session_maker=lambda: MockDBSession(),
        stream_name="test_stream",
        consumer_group="test_group"
    )

    assert hasattr(worker, 'process_message')
    assert callable(worker.process_message)


@pytest.mark.asyncio
async def test_sentiment_worker_has_run():
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "worker"))
    from worker import SentimentWorker

    worker = SentimentWorker(
        redis_client=MockRedis(),
        db_session_maker=lambda: MockDBSession(),
        stream_name="test_stream",
        consumer_group="test_group"
    )

    assert hasattr(worker, 'run')
    assert callable(worker.run)


@pytest.mark.asyncio
async def test_alerting_service_exists():
    from services.alerting import AlertService
    assert AlertService is not None


@pytest.mark.asyncio
async def test_alerting_service_has_check_thresholds():
    from services.alerting import AlertService

    class MockSessionMaker:
        async def __call__(self):
            return MockDBSession()

    alert_service = AlertService(MockSessionMaker())
    assert hasattr(alert_service, 'check_thresholds')
    assert callable(alert_service.check_thresholds)


@pytest.mark.asyncio
async def test_alerting_service_has_save_alert():
    from services.alerting import AlertService

    class MockSessionMaker:
        async def __call__(self):
            return MockDBSession()

    alert_service = AlertService(MockSessionMaker())
    assert hasattr(alert_service, 'save_alert')
    assert callable(alert_service.save_alert)


def test_sentiment_analyzer_analyze_method():
    from services.sentiment_analyzer import SentimentAnalyzer
    analyzer = SentimentAnalyzer(model_type='external')
    result = analyzer.analyze("I love this!")
    assert "sentiment_label" in result
    assert "confidence_score" in result
    assert "model_name" in result
    assert "emotion" in result


def test_sentiment_analyzer_batch_analyze_method():
    from services.sentiment_analyzer import SentimentAnalyzer
    analyzer = SentimentAnalyzer(model_type='external')
    posts = [{"post_id": "1", "content": "Great!"}]
    results = analyzer.batch_analyze(posts)
    assert len(results) == 1
    assert "sentiment_label" in results[0]


@pytest.mark.asyncio
async def test_post_sentiment_variation():
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "ingester"))
    from ingester import DataIngester

    ingester = DataIngester(MockRedis(), posts_per_minute=10)

    positive_keywords = ["love", "amazing", "great", "fantastic", "excellent", "happy", "best"]
    negative_keywords = ["hate", "terrible", "awful", "worst", "disappointed", "horrible"]

    found_positive = False
    found_negative = False

    for _ in range(100):
        post = ingester.generate_post()
        content_lower = post["content"].lower()
        if any(kw in content_lower for kw in positive_keywords):
            found_positive = True
        if any(kw in content_lower for kw in negative_keywords):
            found_negative = True
        if found_positive and found_negative:
            break

    assert found_positive, "Should generate posts with positive keywords"
    assert found_negative, "Should generate posts with negative keywords"


def test_end_to_end_analysis():
    from services.sentiment_analyzer import SentimentAnalyzer

    analyzer = SentimentAnalyzer(model_type='external')

    post = {
        "post_id": "test123",
        "content": "I absolutely love this product! Amazing quality!"
    }

    result = analyzer.analyze(post["content"])

    assert result["sentiment_label"] == "positive"
    assert 0.0 <= result["confidence_score"] <= 1.0
    assert result["emotion"] in ["happy", "angry", "sad", "neutral"]
