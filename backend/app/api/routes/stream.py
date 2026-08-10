"""Server-Sent Events live stream (events + alerts).

Authentication: Bearer token via the Authorization header (preferred) or a
`token` query parameter (legacy / non-header clients). The token is always
validated against the user table (exists + active) and the user's unit scope
is applied so unit admins only receive telemetry for their own unit.
"""

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.deps import get_db, scope_unit_ids
from app.core.exceptions import UnauthorizedError
from app.core.security import decode_access_token
from app.models.user import User
from app.websocket.stream import stream_events

router = APIRouter(tags=["stream"])


def _extract_token(request: Request, query_token: str | None) -> str | None:
    if query_token:
        return query_token
    auth = request.headers.get("authorization")
    if auth and auth.lower().startswith("bearer "):
        return auth[7:].strip()
    return None


@router.get("/stream/live")
async def live_stream(
    request: Request,
    token: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    raw = _extract_token(request, token)
    if not raw:
        raise UnauthorizedError("UNAUTHORIZED", "Missing token")

    try:
        payload = decode_access_token(raw)
    except Exception:
        raise UnauthorizedError("INVALID_TOKEN", "Token is invalid or expired")

    subject = payload.get("sub")
    if not subject:
        raise UnauthorizedError("INVALID_TOKEN", "Token subject missing")

    user = db.get(User, subject)
    if user is None or not user.is_active:
        raise UnauthorizedError("INVALID_TOKEN", "Token is invalid or expired")

    allowed = scope_unit_ids(user)
    return StreamingResponse(
        stream_events(client_id=user.id, allowed_unit_ids=allowed),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
