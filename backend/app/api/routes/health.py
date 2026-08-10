"""Health and system status endpoints."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.database.session import get_db

router = APIRouter(tags=["system"])
settings = get_settings()


@router.get("/health")
def health(db: Session = Depends(get_db)):
    database = "ok"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        database = "error"
    return {
        "status": "ok" if database == "ok" else "degraded",
        "database": database,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
