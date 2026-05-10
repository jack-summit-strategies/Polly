from datetime import datetime, timezone
from typing import Union


# Convert a date string (YYYY-MM-DD) or datetime to a UTC Unix timestamp
def to_unix(date: Union[str, datetime]) -> int:
    if isinstance(date, datetime):
        if date.tzinfo is None:
            date = date.replace(tzinfo=timezone.utc)
        return int(date.timestamp())
    return int(datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp())


# Convert a UTC Unix timestamp to a datetime string (YYYY-MM-DD HH:MM:SS)
def from_unix(timestamp: int) -> str:
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
