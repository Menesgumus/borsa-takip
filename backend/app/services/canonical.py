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
        # Must be UTC. If naive, assume UTC.
        if obj.tzinfo:
            obj = obj.astimezone(timezone.utc)
        return obj.isoformat(timespec='microseconds').replace('+00:00', 'Z')
    elif isinstance(obj, Enum):
        return obj.value
    elif obj is None:
        return None
    elif isinstance(obj, (int, float, str, bool)):
        return obj
    else:
        # Fallback for unexpected objects, try to convert to string representation
        # but warn or just stringify
        return str(obj)

def get_canonical_json(obj: Any) -> str:
    """Returns a deterministic JSON string."""
    return json.dumps(canonicalize(obj), sort_keys=True, separators=(',', ':'))
