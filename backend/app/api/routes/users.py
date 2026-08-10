"""User and role administration."""

import uuid

from fastapi import APIRouter, Depends, Request
from pydantic import EmailStr
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import client_ip, get_current_user, require_permission
from app.core.exceptions import ConflictError, NotFoundError
from app.core.security import hash_password
from app.database.session import get_db
from app.models.user import Role, User
from app.schemas.audit import UserCreate, UserUpdate
from app.schemas.auth import RoleOut, UserOut
from app.services.audit import record_audit

router = APIRouter(tags=["users"])


@router.get("/users")
def list_users(_=Depends(require_permission("users.manage")), user=Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(User).order_by(User.username).all()
    return [UserOut.from_user(u).model_dump() for u in rows]


@router.post("/users", response_model=UserOut, status_code=201)
def create_user(
    body: UserCreate,
    request: Request,
    _=Depends(require_permission("users.manage")),
    admin=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if db.query(User).filter(User.username == body.username).first():
        raise ConflictError("USER_EXISTS", "Username already exists")
    if db.query(User).filter(User.email == body.email).first():
        raise ConflictError("USER_EXISTS", "Email already exists")
    if db.query(Role).filter(Role.id == body.role_id).first() is None:
        raise NotFoundError("ROLE_NOT_FOUND", "Role not found")
    user = User(
        id=uuid.uuid4().hex[:16],
        username=body.username,
        email=body.email,
        full_name=body.full_name,
        password_hash=hash_password(body.password),
        role_id=body.role_id,
        unit_id=body.unit_id,
        is_active=body.is_active,
        must_change_password=True,
    )
    db.add(user)
    record_audit(
        db, "user_created", "users", username=admin.username, user_id=admin.id,
        ip_address=client_ip(request), details={"username": body.username, "role_id": body.role_id},
    )
    db.commit()
    return UserOut.from_user(user)


@router.patch("/users/{user_id}", response_model=UserOut)
def update_user(
    user_id: str,
    body: UserUpdate,
    request: Request,
    _=Depends(require_permission("users.manage")),
    admin=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise NotFoundError("USER_NOT_FOUND", "User not found")

    payload = body.model_dump(exclude_unset=True)

    # Prevent an admin from disabling their own account.
    if payload.get("is_active") is False and user.id == admin.id:
        raise ConflictError("SELF_DISABLE", "You cannot disable your own account")

    # Protect the last active super admin from demotion/disablement.
    is_super = user.role is not None and user.role.name == "super_admin"
    demoting = payload.get("role_id") is not None and payload.get("role_id") != user.role_id
    disabling = payload.get("is_active") is False
    if is_super and (demoting or disabling):
        active_super_admins = (
            db.query(func.count(User.id))
            .join(Role, Role.id == User.role_id)
            .filter(Role.name == "super_admin", User.is_active.is_(True))
            .scalar()
            or 0
        )
        if active_super_admins <= 1:
            raise ConflictError(
                "LAST_SUPER_ADMIN", "Cannot demote or disable the last active super admin"
            )

    changes = {}
    for field, value in payload.items():
        if value is None:
            continue
        if field == "password":
            user.password_hash = hash_password(value)
            user.must_change_password = True
            changes["password"] = "updated"
        elif field == "email":
            try:
                user.email = EmailStr.validate(value)
            except Exception:
                raise ConflictError("INVALID_EMAIL", "Email address is invalid")
            changes["email"] = value
        else:
            setattr(user, field, value)
            changes[field] = value
    db.add(user)
    record_audit(
        db, "user_updated", "users", username=admin.username, user_id=admin.id,
        ip_address=client_ip(request), details={"target": user.username, "changes": changes},
    )
    db.commit()
    return UserOut.from_user(user)


@router.get("/roles")
def list_roles(_=Depends(require_permission("users.manage")), user=Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(Role).order_by(Role.name).all()
    return [RoleOut.model_validate(r).model_dump() for r in rows]
