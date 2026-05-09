from datetime import datetime, timezone


def to_unix(date_str: str) -> int:
    """Convert a date string (YYYY-MM-DD) to a UTC Unix timestamp."""
    return int(datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp())


def from_unix(timestamp: int) -> str:
    """Convert a UTC Unix timestamp to a date string (YYYY-MM-DD)."""
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%Y-%m-%d")
