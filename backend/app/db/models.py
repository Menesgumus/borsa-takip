import enum
import typing

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    profile = relationship("UserProfile", back_populates="user", uselist=False)
    sessions = relationship("Session", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")


class RiskTolerance(enum.StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    timezone = Column(String, default="Europe/Istanbul", nullable=False)
    risk_tolerance: typing.Any = Column(
        Enum(RiskTolerance, name="risktolerance", create_constraint=False, create_type=False),
        nullable=True,
    )
    onboarding_completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user = relationship("User", back_populates="profile")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="sessions")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    action = Column(String, nullable=False, index=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    details = Column(String, nullable=True)  # JSON string or generic text
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="audit_logs")


# ---------------------------------------------------------------------------
# Phase 02 — Instrument Master + Provider Abstraction
# ---------------------------------------------------------------------------


class InstrumentType(enum.StrEnum):
    STOCK = "STOCK"
    ETF = "ETF"
    INDEX = "INDEX"
    CURRENCY = "CURRENCY"
    COMMODITY = "COMMODITY"


class Instrument(Base):
    """Canonical instrument record. Source-agnostic."""

    __tablename__ = "instruments"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True, nullable=False)  # e.g. "BIST:GARAN"
    name = Column(String, nullable=False)
    exchange = Column(String, nullable=False, index=True)  # e.g. "BIST"
    instrument_type: typing.Any = Column(
        Enum(InstrumentType, name="instrumenttype", create_constraint=False, create_type=False),
        nullable=False,
        default=InstrumentType.STOCK,
    )
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    provider_mappings = relationship("ProviderMapping", back_populates="instrument")


class ProviderMapping(Base):
    """Maps a canonical instrument to a provider-specific symbol."""

    __tablename__ = "provider_mappings"

    id = Column(Integer, primary_key=True, index=True)
    instrument_id = Column(
        Integer, ForeignKey("instruments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    provider_name = Column(String, nullable=False, index=True)  # e.g. "mock", "yahoo"
    provider_symbol = Column(String, nullable=False)  # Provider's own symbol
    is_primary = Column(Boolean, default=False, nullable=False)
    priority = Column(Integer, default=0, nullable=False)  # Lower = higher priority
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    instrument = relationship("Instrument", back_populates="provider_mappings")


class ProviderHealth(Base):
    """Circuit-breaker state per provider."""

    __tablename__ = "provider_health"

    provider_name = Column(String, primary_key=True, nullable=False)
    is_healthy = Column(Boolean, default=True, nullable=False)
    last_check_at = Column(DateTime(timezone=True), nullable=True)
    consecutive_failures = Column(Integer, default=0, nullable=False)
    circuit_open = Column(Boolean, default=False, nullable=False)
    circuit_opened_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
