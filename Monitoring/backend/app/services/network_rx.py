import asyncio
import time
import json
from typing import Set
from urllib.request import urlopen

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self._dashboards: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self._dashboards.add(websocket)

    def disconnect(self, websocket: WebSocket):
        try:
            self._dashboards.discard(websocket)
        except Exception:
            pass

    async def broadcast(self, message: str):
        dead = []
        for ws in list(self._dashboards):
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self._dashboards.discard(ws)


manager = ConnectionManager()


async def poll_source(url: str = "http://173.16.0.1:8765/api/rx", interval: float = 1.0):
    """Background poller: fetch source URL periodically and broadcast JSON payloads.

    Broadcast format: {"ts": <epoch>, "data": {<iface>: value, ...}}
    """
    while True:
        try:
            data = await asyncio.to_thread(fetch_json, url)
            if isinstance(data, dict):
                payload = {"ts": time.time(), "data": data}
                await manager.broadcast(json.dumps(payload))
        except Exception:
            # ignore network errors; poll again after sleep
            pass
        await asyncio.sleep(interval)


def fetch_json(url: str):
    with urlopen(url, timeout=5) as response:
        if getattr(response, "status", 200) != 200:
            return None
        raw = response.read().decode("utf-8")
        try:
            return json.loads(raw)
        except Exception:
            return None
