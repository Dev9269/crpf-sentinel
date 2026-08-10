from sqlalchemy import Column, Float, String

from app.database.base import Base, IdMixin, TimestampMixin


class Unit(Base, IdMixin, TimestampMixin):
    __tablename__ = "units"

    unit_code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(120), nullable=False)
    region = Column(String(80), nullable=True)
    city = Column(String(80), nullable=True)
    state = Column(String(80), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    status = Column(String(20), nullable=False, default="operational", index=True)
