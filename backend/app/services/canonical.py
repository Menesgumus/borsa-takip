import json
from decimal import Decimal
from datetime import datetime, timezone
from enum import Enum
from typing import Any

def canonicalize(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: canonicalize(v) for k, v in sorted(obj.items())}
    elif isinstance(obj, list) or isinstance(obj, tuple):
        return [canonicalize(x) for x in obj]
    elif isinstance(obj, Decimal):
        # Format as string explicitly without scientific notation
        return format(obj, 'f')
    elif isinstance(obj, datetime):
        if obj.tzinfo is None:
            raise ValueError("Naive datetimes are not permitted in canonical serialization.")
        obj = obj.astimezone(timezone.utc)
        return obj.isoformat(timespec='microseconds').replace('+00:00', 'Z')
    elif isinstance(obj, Enum):
        return obj.value
    elif obj is None:
        return None
    elif isinstance(obj, (int, float, str, bool)):
        return obj
    else:
        raise TypeError(f"Unsupported type for canonical serialization: {type(obj)}")

def get_canonical_json(obj: Any) -> str:
    """Returns a deterministic JSON string."""
    return json.dumps(canonicalize(obj), sort_keys=True, separators=(',', ':'))
