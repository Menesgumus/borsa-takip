from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
import enum
import typing

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
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
# Phase 02 â€” Instrument Master + Provider Abstraction
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
    historical_daily = relationship(
        "OHLCVDaily", back_populates="instrument", cascade="all, delete-orphan"
    )


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


# ---------------------------------------------------------------------------
# Phase 03 ?" Market Data Ingestion & History
# ---------------------------------------------------------------------------


class OHLCVDaily(Base):
    """Historical daily Open, High, Low, Close, Volume data."""

    __tablename__ = "ohlcv_daily"

    id = Column(Integer, primary_key=True, index=True)
    instrument_id = Column(
        Integer, ForeignKey("instruments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)

    open = Column(Numeric(precision=18, scale=6), nullable=False)
    high = Column(Numeric(precision=18, scale=6), nullable=False)
    low = Column(Numeric(precision=18, scale=6), nullable=False)
    close = Column(Numeric(precision=18, scale=6), nullable=False)
    volume = Column(BigInteger, nullable=True)

    provider_name = Column(String, nullable=True)  # Source of this data point

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    instrument = relationship("Instrument", back_populates="historical_daily")

    __table_args__ = (
        UniqueConstraint("instrument_id", "timestamp", name="uq_ohlcv_daily_instrument_time"),
    )

class KAPDisclosure(Base):
    __tablename__ = "kap_disclosures"

    id = Column(Integer, primary_key=True, index=True)
    instrument_id = Column(Integer, ForeignKey("instruments.id"), nullable=True, index=True)
    disclosure_index = Column(String, unique=True, index=True, nullable=False) # e.g. KAP specific ID
    title = Column(String, nullable=False)
    content_text = Column(Text, nullable=False) # Sanitized factual content
    published_at = Column(DateTime(timezone=True), nullable=False, index=True)

    # Metadata / extraction
    category = Column(String, nullable=True) # e.g. "Finansal Rapor", "Özel Durum Açıklaması"
    provider_sentiment = Column(String, nullable=True) # "POSITIVE", "NEGATIVE", "NEUTRAL"

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class NewsArticle(Base):
    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True, index=True)
    instrument_id = Column(Integer, ForeignKey("instruments.id"), nullable=True, index=True)
    source_id = Column(String, unique=True, index=True, nullable=False) # dedup key
    provider_name = Column(String, nullable=False) # e.g. Bloomberg, Reuters
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=False) # Sanitized
    url = Column(String, nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=False, index=True)

    # Tier / Trust Level
    source_tier = Column(Integer, default=3) # 1=Official/Top, 2=Reputable, 3=Aggregator
    provider_sentiment = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class FundamentalData(Base):
    __tablename__ = "fundamental_data"

    id = Column(Integer, primary_key=True, index=True)
    instrument_id = Column(Integer, ForeignKey("instruments.id"), nullable=False, index=True)
    period = Column(String, nullable=False) # e.g. "2024Q1", "2023FY"

    # Key metrics
    pe_ratio = Column(Numeric(precision=18, scale=6), nullable=True)
    pb_ratio = Column(Numeric(precision=18, scale=6), nullable=True)
    market_cap = Column(Numeric(precision=24, scale=6), nullable=True)
    net_income = Column(Numeric(precision=24, scale=6), nullable=True)
    revenue = Column(Numeric(precision=24, scale=6), nullable=True)

    published_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("instrument_id", "period", name="uq_fundamental_instrument_period"),
    )

class PortfolioType(enum.StrEnum):
    REAL = "REAL"
    PAPER = "PAPER"

class TransactionType(enum.StrEnum):
    BUY = "BUY"
    SELL = "SELL"
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"

class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    portfolio_type = Column(Enum(PortfolioType), nullable=False, default=PortfolioType.PAPER)
    currency = Column(String, default="TRY", nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    transactions = relationship("PortfolioTransaction", back_populates="portfolio", cascade="all, delete-orphan")

class PortfolioTransaction(Base):
    __tablename__ = "portfolio_transactions"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False, index=True)
    instrument_id = Column(Integer, ForeignKey("instruments.id"), nullable=True, index=True) # None for cash movements

    transaction_type = Column(Enum(TransactionType), nullable=False)
    quantity = Column(Numeric(precision=24, scale=8), nullable=False, default=0)
    price = Column(Numeric(precision=18, scale=6), nullable=False, default=0)
    fee = Column(Numeric(precision=18, scale=6), nullable=False, default=0)

    executed_at = Column(DateTime(timezone=True), nullable=False, index=True)

    # Journaling
    notes = Column(Text, nullable=True)
    strategy = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    portfolio = relationship("Portfolio", back_populates="transactions")
from sqlalchemy.sql import func


class TradeJournal(Base):
    __tablename__ = "trade_journals"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False, index=True)
    transaction_id = Column(Integer, ForeignKey("portfolio_transactions.id"), nullable=True, index=True)

    setup = Column(String, nullable=True)
    reason = Column(Text, nullable=True)
    emotion = Column(String, nullable=True)
    lessons_learned = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    portfolio = relationship("Portfolio", backref="journals")
    transaction = relationship("PortfolioTransaction", backref="journal")
