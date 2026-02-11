import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.sentiment_analyzer import SentimentAnalyzer


class TestSentimentAnalyzer:
    @pytest.fixture
    def analyzer(self):
        return SentimentAnalyzer(model_type='external')

    @pytest.mark.asyncio
    async def test_analyzer_has_async_methods(self, analyzer):
        assert hasattr(analyzer, 'analyze_sentiment')
        assert hasattr(analyzer, 'analyze_emotion')
        assert hasattr(analyzer, 'batch_analyze')
        
    @pytest.mark.asyncio
    async def test_analyze_sentiment_structure(self, analyzer):
        result = await analyzer.analyze_sentiment("I love this product!")
        assert "sentiment_label" in result
        assert "confidence_score" in result
        assert "model_name" in result
        assert result["sentiment_label"] in ["positive", "negative", "neutral"]
        assert isinstance(result["confidence_score"], float)

    @pytest.mark.asyncio
    async def test_analyze_emotion_structure(self, analyzer):
        result = await analyzer.analyze_emotion("I am so happy!")
        assert "emotion" in result
        assert "confidence_score" in result
        assert "model_name" in result
        assert result["emotion"] in ["joy", "anger", "sadness", "surprise", "fear", "neutral"]

    @pytest.mark.asyncio
    async def test_positive_sentiment(self, analyzer):
        result = await analyzer.analyze_sentiment("This is amazing! Best thing ever!")
        assert result["sentiment_label"] == "positive"

    @pytest.mark.asyncio
    async def test_negative_sentiment(self, analyzer):
        result = await analyzer.analyze_sentiment("This is terrible! I hate it!")
        assert result["sentiment_label"] == "negative"

    @pytest.mark.asyncio
    async def test_empty_string_neutral(self, analyzer):
        result = await analyzer.analyze_sentiment("")
        assert result["sentiment_label"] == "neutral"
        assert result["confidence_score"] == 0.0

    @pytest.mark.asyncio
    async def test_batch_analyze(self, analyzer):
        texts = ["I love this!", "I hate this!", "It is okay."]
        results = await analyzer.batch_analyze(texts)
        assert len(results) == 3
        assert results[0]["sentiment_label"] == "positive"
        assert results[0]["emotion"] == "joy"
        assert results[1]["sentiment_label"] == "negative"
        assert results[1]["emotion"] == "anger"

    @pytest.mark.asyncio
    async def test_fallback_logic(self, analyzer):
        result = await analyzer.analyze_sentiment("amazing wonderful love")
        assert result["sentiment_label"] == "positive"
