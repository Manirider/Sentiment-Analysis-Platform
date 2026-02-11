from fastapi import APIRouter
from backend.websocket_manager import manager

router = APIRouter()

@router.post("/internal/broadcast")
async def broadcast_sentiment(payload: dict):
    await manager.broadcast(payload)
    return {"status": "sent"}
