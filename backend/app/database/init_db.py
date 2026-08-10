"""Create tables and seed baseline roles + admin user."""

import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.deps import ROLE_PERMISSIONS
from app.core.security import hash_password
from app.database.base import Base
from app.database.session import SessionLocal, engine
from app.models.user import Role, User

settings = get_settings()

ROLE_DESCRIPTIONS = {
    "super_admin": "Full platform control and configuration.",
    "security_expert": "Log analysis, detection and alert investigation.",
    "unit_admin": "Scoped access to a single assigned unit.",
}


def create_tables() -> None:
    import app.models  # noqa: F401  (register all models)

    Base.metadata.create_all(bind=engine)


def seed_roles(db: Session) -> dict[str, Role]:
    roles: dict[str, Role] = {}
    for name, permissions in ROLE_PERMISSIONS.items():
        role = db.query(Role).filter(Role.name == name).first()
        if role is None:
            role = Role(
                id=uuid.uuid4().hex[:16],
                name=name,
                description=ROLE_DESCRIPTIONS.get(name),
                permissions=sorted(permissions),
            )
            db.add(role)
            roles[name] = role
        else:
            role.permissions = sorted(permissions)
            roles[name] = role
    db.commit()
    return roles


def seed_admin(db: Session, roles: dict[str, Role]) -> User | None:
    admin = db.query(User).filter(User.username == settings.SEED_ADMIN_USERNAME).first()
    if admin is None:
        admin = User(
            id=uuid.uuid4().hex[:16],
            username=settings.SEED_ADMIN_USERNAME,
            email=settings.SEED_ADMIN_EMAIL,
            full_name="Platform Administrator",
            password_hash=hash_password(settings.SEED_ADMIN_PASSWORD),
            role_id=roles["super_admin"].id,
            is_active=True,
            must_change_password=True,
            created_at=datetime.now(timezone.utc),
        )
        db.add(admin)
        db.commit()
    return admin


def init_database(seed: bool | None = None) -> None:
    create_tables()
    db: Session = SessionLocal()
    try:
        roles = seed_roles(db)
        seed_admin(db, roles)
    finally:
        db.close()
