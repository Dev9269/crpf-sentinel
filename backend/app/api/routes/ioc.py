"""Indicator of Compromise (IOC) library endpoints."""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.core.deps import client_ip, get_current_user, require_permission
from app.core.exceptions import ConflictError, NotFoundError
from app.database.session import get_db
from app.models.ioc import IocEntry
from app.models.unit import Unit
from app.schemas.ioc import IocCreate, IocOut, IocUpdate
from app.services.audit import record_audit

router = APIRouter(tags=["ioc"])


def _next_ioc_id() -> str:
    return f"IOC-{datetime.now(timezone.utc):%y%m%d}-{uuid.uuid4().hex[:6].upper()}"


def _out(ioc: IocEntry) -> IocOut:
    return IocOut(
        id=ioc.id,
        ioc_id=ioc.ioc_id,
        ioc_type=ioc.ioc_type,
        value=ioc.value,
        description=ioc.description,
        source=ioc.source,
        severity=ioc.severity,
        threat_type=ioc.threat_type,
        reference_url=ioc.reference_url,
        status=ioc.status,
        times_matched=ioc.times_matched,
        last_matched_at=ioc.last_matched_at,
        created_by=ioc.created_by,
        created_at=ioc.created_at,
        updated_at=ioc.updated_at,
    )


@router.get("/ioc")
def list_iocs(
    ioc_type: str | None = Query(None),
    severity: str | None = Query(None),
    status: str | None = Query(None),
    q: str | None = Query(None, max_length=200),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
    _=Depends(require_permission("threat_intel.view")),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(IocEntry)
    if ioc_type:
        query = query.filter(IocEntry.ioc_type == ioc_type)
    if severity:
        query = query.filter(IocEntry.severity == severity)
    if status:
        query = query.filter(IocEntry.status == status)
    if q:
        like = f"%{q}%"
        query = query.filter(
            func.lower(IocEntry.value).like(like)
            | func.lower(IocEntry.ioc_id).like(like)
            | func.lower(IocEntry.description).like(like)
        )

    total = query.count()
    rows = (
        query.order_by(IocEntry.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {
        "items": [_out(i).model_dump() for i in rows],
        "meta": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (total + page_size - 1) // page_size,
        },
    }


@router.post("/ioc", response_model=IocOut, status_code=201)
def create_ioc(
    body: IocCreate,
    request: Request,
    _=Depends(require_permission("threat_intel.manage")),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    normalized = body.value.strip().lower()
    exists = (
        db.query(IocEntry)
        .filter(IocEntry.ioc_type == body.ioc_type, func.lower(IocEntry.value) == normalized)
        .first()
    )
    if exists:
        raise ConflictError("IOC_EXISTS", f"IOC already exists: {body.value}")

    ioc = IocEntry(
        id=uuid.uuid4().hex[:16],
        ioc_id=_next_ioc_id(),
        ioc_type=body.ioc_type,
        value=normalized,
        description=body.description,
        source=body.source,
        severity=body.severity,
        threat_type=body.threat_type,
        reference_url=body.reference_url,
        status=body.status,
        created_by=user.id,
    )
    db.add(ioc)
    record_audit(
        db, "ioc_created", "ioc",
        username=user.username, user_id=user.id, ip_address=client_ip(request),
        details={"ioc_id": ioc.ioc_id, "ioc_type": ioc.ioc_type, "value": ioc.value},
    )
    db.commit()
    return _out(ioc)


@router.patch("/ioc/{ioc_id}", response_model=IocOut)
def update_ioc(
    ioc_id: str,
    body: IocUpdate,
    request: Request,
    _=Depends(require_permission("threat_intel.manage")),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ioc = db.query(IocEntry).filter(or_(IocEntry.id == ioc_id, IocEntry.ioc_id == ioc_id)).first()
    if ioc is None:
        raise NotFoundError("IOC_NOT_FOUND", "IOC entry not found")
    for field in ("description", "source", "severity", "threat_type", "reference_url", "status"):
        value = getattr(body, field, None)
        if value is not None:
            setattr(ioc, field, value)
    db.add(ioc)
    record_audit(
        db, "ioc_updated", "ioc",
        username=user.username, user_id=user.id, ip_address=client_ip(request),
        details={"ioc_id": ioc.ioc_id},
    )
    db.commit()
    return _out(ioc)


@router.delete("/ioc/{ioc_id}", status_code=204)
def delete_ioc(
    ioc_id: str,
    request: Request,
    _=Depends(require_permission("threat_intel.manage")),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ioc = db.query(IocEntry).filter(or_(IocEntry.id == ioc_id, IocEntry.ioc_id == ioc_id)).first()
    if ioc is None:
        raise NotFoundError("IOC_NOT_FOUND", "IOC entry not found")
    record_audit(
        db, "ioc_deleted", "ioc",
        username=user.username, user_id=user.id, ip_address=client_ip(request),
        details={"ioc_id": ioc.ioc_id},
    )
    db.delete(ioc)
    db.commit()
    return None
