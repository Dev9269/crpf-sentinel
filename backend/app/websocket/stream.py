"""Server-Sent Events broadcast hub.

Each connected dashboard client receives a `data:` line whenever a new
event is ingested or a new alert is raised. No polling required.

Subscribers may be scoped to a set of unit ids; messages whose payload has a
`unit_id` outside that scope are dropped for that subscriber.
"""

import asyncio
import json
from typing import Any

from app.core.config import get_settings

settings = get_settings()

_subscribers: list[tuple[asyncio.Queue, set[str] | None]] = []


async def subscribe(allowed_unit_ids: set[str] | None = None) -> asyncio.Queue:
    queue: asyncio.Queue = asyncio.Queue(maxsize=500)
    _subscribers.append((queue, allowed_unit_ids))
    return queue


def unsubscribe(queue: asyncio.Queue) -> None:
    _subscribers[:] = [(q, scope) for (q, scope) in _subscribers if q is not queue]


def publish(kind: str, payload: dict[str, Any]) -> None:
    message = json.dumps({"kind": kind, "data": payload})
    for queue, allowed in list(_subscribers):
        if allowed is not None:
            unit_id = payload.get("unit_id")
            if not unit_id or unit_id not in allowed:
                continue
        try:
            queue.put_nowait(message)
        except asyncio.QueueFull:
            try:
                queue.get_nowait()
                queue.put_nowait(message)
            except Exception:
                pass


async def stream_events(client_id: str, allowed_unit_ids: list[str] | None = None):
    """Async generator for the /api/stream/live endpoint."""
    queue = await subscribe(set(allowed_unit_ids) if allowed_unit_ids else None)
    try:
        yield f"event: connected\ndata: {{\"client\":\"{client_id}\"}}\n\n"
        while True:
            message = await queue.get()
            yield f"event: message\ndata: {message}\n\n"
    finally:
        unsubscribe(queue)
