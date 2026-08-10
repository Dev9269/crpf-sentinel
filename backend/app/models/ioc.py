"""Indicator of Compromise (IOC) library.

Threat-intel indicators (IPs, domains, hashes, URLs, commands) that are
matched against inbound normalized events in addition to signature rules.
"""

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.database.base import Base, IdMixin, TimestampMixin


class IocEntry(Base, IdMixin, TimestampMixin):
    __tablename__ = "ioc_entries"

    ioc_id = Column(String(40), unique=True, nullable=False, index=True)
    ioc_type = Column(String(20), nullable=False, index=True)  # ip | domain | hash | url | command
    value = Column(String(512), nullable=False, index=True)
    description = Column(Text, nullable=True)
    source = Column(String(60), nullable=False, default="manual")
    severity = Column(String(20), nullable=False, default="medium")
    threat_type = Column(String(60), nullable=True)
    reference_url = Column(String(512), nullable=True)
    status = Column(String(20), nullable=False, default="enabled", index=True)
    times_matched = Column(Integer, nullable=False, default=0)
    last_matched_at = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(String(32), nullable=True)
