import os
import asyncio
from typing import List
from functools import partial

class SentimentAnalyzer:
    _local_sentiment_pipeline = None
    _local_emotion_pipeline = None

    def __init__(self, model_type: str = 'local', model_name: str = None):
        self.model_type = model_type
        self.model_name = model_name or os.getenv(
            "HUGGINGFACE_MODEL",
            "distilbert-base-uncased-finetuned-sst-2-english"
        )
        self.emotion_model = os.getenv(
            "EMOTION_MODEL",
            "j-hartmann/emotion-english-distilroberta-base"
        )

        if model_type == 'local':
            self._init_local_models()

    def _init_local_models(self):
        try:
            from transformers import pipeline

            if SentimentAnalyzer._local_sentiment_pipeline is None:
                print("Loading sentiment model...")
                SentimentAnalyzer._local_sentiment_pipeline = pipeline(
                    "sentiment-analysis",
                    model=self.model_name,
                    device=-1
                )

            if SentimentAnalyzer._local_emotion_pipeline is None:
                print("Loading emotion model...")
                try:
                    SentimentAnalyzer._local_emotion_pipeline = pipeline(
                        "text-classification",
                        model=self.emotion_model,
                        top_k=1,
                        device=-1
                    )
                except Exception:
                    SentimentAnalyzer._local_emotion_pipeline = None
        except Exception as e:
            print(f"Failed to load models: {e}")

    async def analyze_sentiment(self, text: str) -> dict:
        if not text or not text.strip():
            return {
                "sentiment_label": "neutral",
                "confidence_score": 0.0,
                "model_name": self.model_name
            }

        text = text[:512]
        
        if self.model_type == 'local' and SentimentAnalyzer._local_sentiment_pipeline:
            loop = asyncio.get_running_loop()
            try:
                result = await loop.run_in_executor(
                    None, 
                    partial(SentimentAnalyzer._local_sentiment_pipeline, text)
                )
                sentiment_result = result[0]
                label = sentiment_result["label"].lower()
                confidence = float(sentiment_result["score"])

                if confidence < 0.6:
                    sentiment_label = "neutral"
                elif label == "positive":
                    sentiment_label = "positive"
                elif label == "negative":
                    sentiment_label = "negative"
                else:
                    sentiment_label = "neutral"
                
                return {
                    "sentiment_label": sentiment_label,
                    "confidence_score": min(max(confidence, 0.0), 1.0),
                    "model_name": self.model_name
                }
            except Exception:
                pass
        

        label, score = self._fallback_sentiment(text)
        return {
            "sentiment_label": label,
            "confidence_score": score,
            "model_name": self.model_name
        }

    async def analyze_emotion(self, text: str) -> dict:
        if not text or not text.strip():
            return {
                "emotion": "neutral",
                "confidence_score": 0.0,
                "model_name": self.emotion_model
            }
            
        text = text[:512]

        if self.model_type == 'local' and SentimentAnalyzer._local_emotion_pipeline:
            loop = asyncio.get_running_loop()
            try:
                result = await loop.run_in_executor(
                    None,
                    partial(SentimentAnalyzer._local_emotion_pipeline, text)
                )
                emotion_result = result[0][0]
                emotion_label = emotion_result["label"].lower()
                confidence = float(emotion_result["score"])
                mapped_emotion = self._map_emotion(emotion_label)

                return {
                    "emotion": mapped_emotion,
                    "confidence_score": min(max(confidence, 0.0), 1.0),
                    "model_name": self.emotion_model
                }
            except Exception:
                pass


        emotion = self._fallback_emotion(text)
        return {
            "emotion": emotion,
            "confidence_score": 0.7,
            "model_name": self.emotion_model
        }

    async def batch_analyze(self, texts: List[str]) -> List[dict]:
        if not texts:
            return []
        
        tasks = []
        for text in texts:
            tasks.append(self._analyze_full(text))
            
        return await asyncio.gather(*tasks)

    async def _analyze_full(self, text: str) -> dict:
        sentiment_task = asyncio.create_task(self.analyze_sentiment(text))
        emotion_task = asyncio.create_task(self.analyze_emotion(text))
        
        sentiment, emotion = await asyncio.gather(sentiment_task, emotion_task)
        
        return {
            "sentiment_label": sentiment["sentiment_label"],
            "confidence_score": sentiment["confidence_score"],
            "model_name": sentiment["model_name"],
            "emotion": emotion["emotion"]
        }

    def _map_emotion(self, emotion: str) -> str:
        emotion_map = {
            "joy": "joy",
            "happiness": "joy",
            "love": "joy",
            "anger": "anger",
            "annoyance": "anger",
            "disgust": "anger",
            "sadness": "sadness",
            "grief": "sadness",
            "disappointment": "sadness",
            "fear": "fear",
            "nervousness": "fear",
            "surprise": "surprise",
            "neutral": "neutral",
        }
        return emotion_map.get(emotion, "neutral")

    def _fallback_sentiment(self, text: str) -> tuple:
        positive_words = ["love", "great", "amazing", "excellent", "fantastic", "happy", "best", "wonderful", "awesome"]
        negative_words = ["hate", "terrible", "awful", "worst", "disappointed", "horrible", "bad", "angry", "sad"]

        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)

        if pos_count > neg_count:
            return "positive", 0.85
        elif neg_count > pos_count:
            return "negative", 0.85
        else:
            return "neutral", 0.70

    def _fallback_emotion(self, text: str) -> str:
        text_lower = text.lower()
        if any(w in text_lower for w in ["happy", "love", "great", "amazing", "excited", "joy"]):
            return "joy"
        elif any(w in text_lower for w in ["angry", "hate", "furious", "mad"]):
            return "anger"
        elif any(w in text_lower for w in ["sad", "disappointed", "depressed", "unhappy"]):
            return "sadness"
        elif "wow" in text_lower or "surprise" in text_lower:
            return "surprise"
        elif "scared" in text_lower or "fear" in text_lower:
            return "fear"
        else:
            return "neutral"
