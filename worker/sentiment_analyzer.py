from transformers import pipeline

class SentimentAnalyzer:
    def __init__(self):
        print("Loading Sentiment Model...")
        self.sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english"
        )
        print("Loading Emotion Model...")
        self.emotion_pipeline = pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            top_k=1
        )

    def analyze(self, text: str):
        sent_result = self.sentiment_pipeline(text[:512])[0]
        
        confidence = float(sent_result["score"])
        if confidence < 0.70:
            sentiment = "neutral"
        else:
            sentiment = sent_result["label"].lower()
        
        emo_result = self.emotion_pipeline(text[:512])[0][0]
        
        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "emotion": emo_result["label"].lower()
        }
