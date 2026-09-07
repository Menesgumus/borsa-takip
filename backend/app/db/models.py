import enum
from sqlalchemy.sql import func
import typing

from sqlalchemy import Numeric
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
    period_end = Column(DateTime(timezone=True), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    available_at = Column(DateTime(timezone=True), nullable=True)
    source = Column(String, nullable=True)

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


class DecisionAction(enum.StrEnum):
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"

class DecisionSnapshot(Base):
    __tablename__ = "decision_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    instrument_id = Column(Integer, ForeignKey("instruments.id"), nullable=False, index=True)
    action = Column(Enum(DecisionAction), nullable=False)

    score = Column(Numeric(10, 4), nullable=False) # Normalized score -1.0 to 1.0
    engine_version = Column(String, nullable=False) # e.g. "v1.0"
    reason_codes = Column(String, nullable=False) # e.g. "RSI_OVERSOLD,MACD_BULLISH"

    calculated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    instrument = relationship("Instrument", backref="decisions")
class ChatThread(Base):
    __tablename__ = "chat_threads"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    messages = relationship("ChatMessage", back_populates="thread", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(Integer, ForeignKey("chat_threads.id"), nullable=False, index=True)
    role = Column(String, nullable=False) # "user", "assistant", "system"
    content = Column(Text, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    thread = relationship("ChatThread", back_populates="messages")
class EducationalModule(Base):
    __tablename__ = "educational_modules"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    category = Column(String, nullable=False) # e.g. "TECHNICAL_ANALYSIS", "FUNDAMENTALS", "PORTFOLIO"
    display_order = Column(Integer, default=0)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    lessons = relationship("EducationalLesson", back_populates="module", order_by="EducationalLesson.display_order")

class EducationalLesson(Base):
    __tablename__ = "educational_lessons"

    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("educational_modules.id"), nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    summary = Column(String, nullable=True)
    
    content_beginner = Column(Text, nullable=False) # Simple Explanation
    content_detailed = Column(Text, nullable=False) # Market interpretation, risks, caveats
    
    key_points = Column(String, nullable=True) # JSON or comma separated
    related_terms = Column(String, nullable=True)
    
    display_order = Column(Integer, default=0)
    estimated_minutes = Column(Integer, default=5)
    version = Column(Integer, default=1)
    is_published = Column(Boolean, default=True)

    module = relationship("EducationalModule", back_populates="lessons")
    progresses = relationship("UserLessonProgress", back_populates="lesson", cascade="all, delete-orphan")

class UserLessonProgress(Base):
    __tablename__ = "user_lesson_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    lesson_id = Column(Integer, ForeignKey("educational_lessons.id"), nullable=False, index=True)
    
    is_completed = Column(Boolean, default=False)
    last_position = Column(String, nullable=True) # bookmark
    
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    lesson = relationship("EducationalLesson", back_populates="progresses")
import enum

class AlertType(enum.Enum):
    PRICE = "PRICE"
    RSI = "RSI"
    KAP = "KAP"
    NEWS = "NEWS"
    DECISION = "DECISION"
    CONCENTRATION = "CONCENTRATION"
    DAILY_LOSS = "DAILY_LOSS"

class AlertRule(Base):
    __tablename__ = "alert_rules"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    alert_type = Column(Enum(AlertType), nullable=False)
    instrument_id = Column(Integer, ForeignKey("instruments.id"), nullable=True) # None for portfolio-wide alerts
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=True)
    
    operator = Column(String, nullable=True) # e.g. ">", "<", "=="
    threshold = Column(Numeric(precision=24, scale=6), nullable=True)
    config_data = Column(String, nullable=True) # JSON payload for extra config
    
    is_enabled = Column(Boolean, default=True)
    cooldown_minutes = Column(Integer, default=60) # Default 1h
    
    last_triggered_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", backref="alert_rules")

class UserNotification(Base):
    __tablename__ = "user_notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    rule_id = Column(Integer, ForeignKey("alert_rules.id", ondelete="SET NULL"), nullable=True)
    
    alert_type = Column(Enum(AlertType), nullable=False)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    trigger_data = Column(String, nullable=True) # JSON
    
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", backref="notifications")
class BacktestJob(Base):
    __tablename__ = "backtest_jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Configuration
    strategy_name = Column(String, nullable=False)
    strategy_version = Column(String, nullable=False)
    
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    
    initial_capital = Column(Numeric(precision=24, scale=6), nullable=False)
    
    # Costs
    commission_pct = Column(Numeric(precision=10, scale=6), nullable=False, default=0.001) # 0.1%
    slippage_pct = Column(Numeric(precision=10, scale=6), nullable=False, default=0.0005)  # 0.05%
    
    # Status tracking
    status = Column(String, nullable=False, default="PENDING") # PENDING, RUNNING, COMPLETED, FAILED
    failure_reason = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    result = relationship("BacktestResult", back_populates="job", uselist=False)

class BacktestResult(Base):
    __tablename__ = "backtest_results"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("backtest_jobs.id"), nullable=False, unique=True)
    
    # Final Metrics
    total_return_pct = Column(Numeric(precision=10, scale=6), nullable=True)
    cagr_pct = Column(Numeric(precision=10, scale=6), nullable=True)
    max_drawdown_pct = Column(Numeric(precision=10, scale=6), nullable=True)
    
    win_rate_pct = Column(Numeric(precision=10, scale=6), nullable=True)
    total_trades = Column(Integer, nullable=True)
    fees_paid = Column(Numeric(precision=24, scale=6), nullable=True)
    
    # Benchmark
    benchmark_return_pct = Column(Numeric(precision=10, scale=6), nullable=True)
    
    # JSON Data Series
    equity_curve = Column(Text, nullable=True) # e.g. [{"date": "...", "equity": ...}]
    bias_audit = Column(Text, nullable=True) # e.g. {"LOOK_AHEAD": "PASS", "SURVIVORSHIP": "UNVERIFIED"}
    limitations = Column(Text, nullable=True) # e.g. ["HISTORICAL_UNIVERSE_UNAVAILABLE"]
    validation_state = Column(String, nullable=True) # VALIDATED, LIMITED, UNVERIFIED

    job = relationship("BacktestJob", back_populates="result")
    trades = relationship("BacktestTrade", back_populates="result")

class BacktestTrade(Base):
    __tablename__ = "backtest_trades"

    id = Column(Integer, primary_key=True, index=True)
    result_id = Column(Integer, ForeignKey("backtest_results.id"), nullable=False, index=True)
    
    instrument_symbol = Column(String, nullable=False)
    direction = Column(String, nullable=False) # BUY, SELL
    
    executed_at = Column(DateTime(timezone=True), nullable=False)
    quantity = Column(Numeric(precision=18, scale=6), nullable=False)
    price = Column(Numeric(precision=18, scale=6), nullable=False)
    
    fees = Column(Numeric(precision=18, scale=6), nullable=False)
    slippage = Column(Numeric(precision=18, scale=6), nullable=False)
    
    result = relationship("BacktestResult", back_populates="trades")
class StrategyVersion(Base):
    __tablename__ = "strategy_versions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    version = Column(String, nullable=False, unique=True)
    status = Column(String, nullable=False) # CHAMPION, CHALLENGER, DEPRECATED
    config_json = Column(Text, nullable=False) # Weights, params
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    promoted_at = Column(DateTime(timezone=True), nullable=True)
    promotion_reason = Column(String, nullable=True) # E.g., "BLOCKED_BY_DATA_VALIDATION" if attempted

class DecisionOutcome(Base):
    __tablename__ = "decision_outcomes"

    id = Column(Integer, primary_key=True, index=True)
    decision_id = Column(Integer, ForeignKey("decision_snapshots.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # Forward Returns (in percentage)
    return_t1 = Column(Numeric(precision=10, scale=6), nullable=True)
    return_t5 = Column(Numeric(precision=10, scale=6), nullable=True)
    return_t20 = Column(Numeric(precision=10, scale=6), nullable=True)
    return_t60 = Column(Numeric(precision=10, scale=6), nullable=True)
    
    # Benchmark Returns (in percentage)
    benchmark_t1 = Column(Numeric(precision=10, scale=6), nullable=True)
    benchmark_t5 = Column(Numeric(precision=10, scale=6), nullable=True)
    benchmark_t20 = Column(Numeric(precision=10, scale=6), nullable=True)
    benchmark_t60 = Column(Numeric(precision=10, scale=6), nullable=True)

    evaluated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    decision = relationship("DecisionSnapshot", backref="outcome")
class BehaviorProfile(Base):
    __tablename__ = "behavior_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    fomo_tendency_score = Column(Numeric(5, 2), default=0) # 0 to 100
    patience_score = Column(Numeric(5, 2), default=0) # 0 to 100
    concentration_risk = Column(Numeric(5, 2), default=0) # 0 to 100
    
    last_analyzed_at = Column(DateTime(timezone=True), server_default=func.now())

class TradeInsight(Base):
    __tablename__ = "trade_insights"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    transaction_id = Column(Integer, ForeignKey("portfolio_transactions.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    insight_type = Column(String, nullable=False) # e.g. "FOMO_ENTRY", "EARLY_EXIT", "CONCENTRATION_WARNING"
    description = Column(String, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
