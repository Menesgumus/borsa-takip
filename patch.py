import sys

with open("backend/app/db/models.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if "from sqlalchemy import (" in line:
        new_lines.append(line)
        new_lines.append("    JSON,\n")
    elif "slippage_pct = Column(Numeric" in line:
        new_lines.append(line)
        new_lines.append("""
    # Phase 30 Governance Metadata
    calibration_cycle_id = Column(Integer, ForeignKey("calibration_cycles.id", ondelete="SET NULL"), nullable=True)
    code_commit_sha = Column(String(40), nullable=True)
    engine_ver = Column(String(50), nullable=True)
    lifecycle_ver = Column(String(50), nullable=True)
    alloc_ver = Column(String(50), nullable=True)
    exec_ver = Column(String(50), nullable=True)
    metric_ver = Column(String(50), nullable=True)
    cal_ver = Column(String(50), nullable=True)
    config_hash = Column(String(64), nullable=True)
    frozen_challenger_manifest_hash = Column(String(64), nullable=True)
    dataset_root_hash = Column(String(64), nullable=True)
    universe_fingerprint = Column(String(64), nullable=True)
    benchmark_id = Column(String(50), nullable=True)
    asset_classes = Column(JSON, nullable=True)
    base_currency = Column(String(10), nullable=True)
    cost_model = Column(String(50), nullable=True)
    seed = Column(Integer, nullable=True)
    role = Column(String(20), nullable=False, server_default="TRAIN")
""")
    elif "decision = relationship(" in line:
        new_lines.append("""
    status = Column(String(50), nullable=False, server_default="UNTRUSTED_LEGACY_OUTCOME")
    provenance_metadata = Column(JSON, nullable=True)
""")
        new_lines.append(line)
    elif "class BehaviorProfile" in line:
        new_lines.append("""
class IdempotencyRecord(Base):
    __tablename__ = "idempotency_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=True)
    mutation_family = Column(String(50), nullable=False)
    idempotency_key = Column(String(100), nullable=False)
    request_hash = Column(String(64), nullable=False)
    response_payload = Column(JSON, nullable=True)
    status = Column(String(20), nullable=False) # e.g. "COMPLETED", "FAILED"
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "mutation_family", "idempotency_key", name="uix_idempotency_key"),
    )

class CalibrationCycle(Base):
    __tablename__ = "calibration_cycles"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String(50), nullable=False) # e.g. "OPEN", "FROZEN", "HOLDOUT_CONSUMED"
    champion_config_hash = Column(String(64), nullable=True)
    frozen_challenger_manifest_hash = Column(String(64), nullable=True)
    train_interval_start = Column(DateTime, nullable=True)
    train_interval_end = Column(DateTime, nullable=True)
    validation_interval_start = Column(DateTime, nullable=True)
    validation_interval_end = Column(DateTime, nullable=True)
    holdout_interval_start = Column(DateTime, nullable=True)
    holdout_interval_end = Column(DateTime, nullable=True)
    
    locked_at = Column(DateTime(timezone=True), nullable=True)
    validation_completed_at = Column(DateTime(timezone=True), nullable=True)
    holdout_opened_at = Column(DateTime(timezone=True), nullable=True)
    holdout_consumed_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

""")
        new_lines.append(line)
    else:
        new_lines.append(line)

with open("backend/app/db/models.py", "w", encoding="utf-8") as f:
    f.writelines(new_lines)
