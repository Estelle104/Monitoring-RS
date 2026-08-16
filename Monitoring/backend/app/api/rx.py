from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.network_rx import manager

router = APIRouter()


@router.websocket("/ws/netmetrics")
async def ws_netmetrics(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # keep connection open; clients may send pings or messages
            try:
                await websocket.receive_text()
            except WebSocketDisconnect:
                break
    finally:
        manager.disconnect(websocket)
