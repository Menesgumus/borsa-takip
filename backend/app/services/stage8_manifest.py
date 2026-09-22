import hashlib
import json
from decimal import Decimal
from typing import Any

from app.services.canonical import get_canonical_json

CHAMPION_CONFIG = {
    "WATCH_THRESHOLD": 1,
    "CONFIRMED_THRESHOLD": 3,
    "EXIT_THRESHOLD": 5,
    "STRONG_EXIT_THRESHOLD": 3,
    "RECOVERY_THRESHOLD": 2,
    "ADD_THRESHOLD": 2,
    "REDUCE_FRACTION": "0.5",
    "MAX_CONCENTRATION_LIMIT": "0.3"
}

def get_champion_hash() -> str:
    return hashlib.sha256(get_canonical_json(CHAMPION_CONFIG).encode('utf-8')).hexdigest()

def generate_challenger_manifest() -> list[dict]:
    champ_hash = get_champion_hash()
    manifest = []
    
    # 1 variable at a time variants
    variants = [
        ("WATCH_THRESHOLD", 2, "WATCH_2"),
        ("CONFIRMED_THRESHOLD", 2, "DETERIORATION_2"),
        ("CONFIRMED_THRESHOLD", 4, "DETERIORATION_4"),
        ("EXIT_THRESHOLD", 4, "EXIT_NEG_4"),
        ("EXIT_THRESHOLD", 6, "EXIT_NEG_6"),
        ("STRONG_EXIT_THRESHOLD", 2, "EXIT_STRONG_SELL_2"),
        ("STRONG_EXIT_THRESHOLD", 4, "EXIT_STRONG_SELL_4"),
        ("RECOVERY_THRESHOLD", 1, "RECOVERY_1"),
        ("RECOVERY_THRESHOLD", 3, "RECOVERY_3"),
        ("ADD_THRESHOLD", 1, "ADD_1"),
        ("ADD_THRESHOLD", 3, "ADD_3"),
        ("REDUCE_FRACTION", "0.25", "REDUCE_25"),
        ("REDUCE_FRACTION", "0.75", "REDUCE_75"),
    ]
    
    for key, new_val, name in variants:
        manifest.append({
            "candidate_id": name,
            "base_champion_hash": champ_hash,
            "changed_parameter": key,
            "champion_value": CHAMPION_CONFIG[key],
            "challenger_value": new_val,
            "unchanged_policy_references": "v1_event_safe"
        })
        
    return manifest

def get_challenger_manifest_hash() -> str:
    manifest = generate_challenger_manifest()
    return hashlib.sha256(get_canonical_json(manifest).encode('utf-8')).hexdigest()
