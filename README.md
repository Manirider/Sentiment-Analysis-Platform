# Real-Time Sentiment Analysis Platform

A distributed microservices platform for real-time sentiment analysis of social media content. The system ingests posts, processes them through AI models, and delivers live analytics via a React dashboard.

Built with FastAPI, React, PostgreSQL, Redis Streams, and HuggingFace Transformers.

## Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Ingester   │───▶│    Redis    │───▶│   Worker    │
│             │    │   Streams   │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
                                            │
                                            ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Frontend   │◀──▶│   Backend   │◀──▶│ PostgreSQL  │
│   :3000     │    │    :8000    │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
```

The platform runs six containerized services:

| Service | Port | Role |
|---------|------|------|
| postgres | - | Persistent storage |
| redis | - | Message queue (Redis Streams) |
| ingester | - | Generates and publishes posts |
| worker | - | Runs AI analysis, stores results |
| backend | 8000 | REST API + WebSocket server |
| frontend | 3000 | React dashboard |

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system design.

## Key Features

- **Real-time Processing** — Posts flow through Redis Streams with consumer group semantics
- **Dual AI Models** — HuggingFace sentiment + emotion classifiers with fallback logic
- **Live Dashboard** — WebSocket-powered React UI with live charts and feed
- **Alert System** — Monitors sentiment trends and triggers threshold-based alerts
- **Scalable Design** — Stateless workers, connection pooling, async everywhere

## Prerequisites

- Docker 20.10+ and Docker Compose 2.0+
- 4GB RAM minimum
- Ports 3000 and 8000 available

## Quick Start

```bash
# Clone and configure
git clone <repo-url>
cd sentiment-platform
cp .env.example .env

# Start all services
docker-compose up -d

# Wait for services (~30-60 seconds)
docker-compose ps

# Verify
curl http://localhost:8000/api/health

# Access dashboard
open http://localhost:3000
```

## API Reference

### REST Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Service health with stats |
| `/api/posts` | GET | Paginated posts (`?limit=50&offset=0`) |
| `/api/analytics` | GET | Sentiment distribution and counts |

### WebSocket

Connect to `ws://localhost:8000/ws/sentiment` for real-time updates.

Events:
- `connected` — Connection confirmed
- `new_post` — Post analyzed and ready
- `metrics_update` — Aggregate metrics (every 30s)

## Core Components

### DataIngester
Generates synthetic social media posts and publishes to Redis Stream.

```python
ingester = DataIngester(redis_client, posts_per_minute=10)
await ingester.start()
```

### SentimentAnalyzer
Runs sentiment and emotion classification using HuggingFace models with automatic fallback.

```python
analyzer = SentimentAnalyzer(model_type='local')
result = await analyzer.analyze_sentiment("Great product!")
# → {sentiment_label: "positive", confidence_score: 0.95, emotion: "joy"}
```

### SentimentWorker
Consumes posts from Redis Stream, processes through analyzer, persists to PostgreSQL.

```python
worker = SentimentWorker(redis_client, db_session_maker, stream_name, group_name)
await worker.run(batch_size=10)
```

### AlertService
Monitors sentiment ratios and generates alerts when thresholds are exceeded.

```python
alert_service = AlertService(db_session_maker, redis_client)
await alert_service.run_monitoring_loop(check_interval_seconds=60)
```

## Testing

```bash
# All tests with coverage
docker-compose exec backend pytest -v --cov=backend

# Specific suite
docker-compose exec backend pytest tests/test_sentiment.py -v

# Integration tests
docker-compose exec backend pytest tests/test_integration.py -v
```

## Project Structure

```
sentiment-platform/
├── docker-compose.yml
├── .env.example
├── README.md
├── ARCHITECTURE.md
├── backend/
│   ├── main.py                 # FastAPI app, routes, WebSocket
│   ├── database.py             # SQLAlchemy async setup
│   ├── models/models.py        # ORM models
│   ├── services/
│   │   ├── sentiment_analyzer.py
│   │   └── alerting.py
│   └── tests/
├── worker/
│   └── worker.py               # Redis consumer, batch processing
├── ingester/
│   └── ingester.py             # Post generation, Redis publisher
└── frontend/
    └── src/
        ├── pages/              # Dashboard, Analytics, LiveFeed
        ├── components/         # Charts, cards, feed widgets
        └── services/api.js     # API client, WebSocket handler
```

## Troubleshooting

```bash
# Check service logs
docker-compose logs backend

# Restart specific service
docker-compose restart worker

# Database connectivity
docker-compose exec postgres pg_isready -U sentiment_user

# Redis connectivity
docker-compose exec redis redis-cli ping
```

## Tech Stack

| Layer | Technology |
|-------|------------|
| API | FastAPI (async, WebSocket) |
| Frontend | React + Vite + Recharts |
| Database | PostgreSQL 15 |
| Queue | Redis 7 Streams |
| AI | HuggingFace Transformers |
| Container | Docker Compose |

## Author

**suryasai**

## License

MIT