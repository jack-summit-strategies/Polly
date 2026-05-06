from __future__ import annotations

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Request
# ---------------------------------------------------------------------------

class PriceHistoryParams(BaseModel):
    market: str                             # CLOB token ID
    startTs: int | None = None              # Unix timestamp (seconds)
    endTs: int | None = None                # Unix timestamp (seconds)
    fidelity: int | None = Field(default=None, ge=1)  # resolution in minutes


# ---------------------------------------------------------------------------
# Response
# ---------------------------------------------------------------------------

class PricePoint(BaseModel):
    t: int      # Unix timestamp
    p: float    # price


class PriceHistory(BaseModel):
    history: list[PricePoint]
