from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field


class EventType(str, Enum):
    TRADE = "trade"
    SPLIT = "split"
    MERGE = "merge"
    REDEEM = "redeem"


# ---------------------------------------------------------------------------
# Request
# ---------------------------------------------------------------------------

class MarketActivityParams(BaseModel):
    user: str | None = Field(default=None, pattern=r"^(0[xX])?[0-9a-fA-F]{40}$")
    token_id: str | None = None
    condition_id: str | None = None
    event_type: EventType | None = None
    start_time: str = "1577836800"  # 2020-01-01
    end_time: str = "1893456000"    # 2030-01-01
    limit: int | None = Field(default=10, ge=1, le=1000)
    page: int | None = Field(default=1, ge=1, le=767465558638)


# ---------------------------------------------------------------------------
# Response
# ---------------------------------------------------------------------------

class TokenActivityMarket(BaseModel):
    condition_id: str | None = None
    market_slug: str | None = None
    token_id: str | None = None
    outcome_label: str | None = None
    closed: bool | None = None


class TokenActivity(BaseModel):
    event_type: str | None = None
    timestamp: str | None = None
    block_num: int | None = None
    tx_hash: str | None = None
    user: str | None = None
    amount: str | None = None
    value: float | None = None
    fee_amount: str | None = None
    fee_value: float | None = None
    market: TokenActivityMarket | None = None


class MarketActivityResponse(BaseModel):
    data: list[TokenActivity] = Field(default_factory=list)