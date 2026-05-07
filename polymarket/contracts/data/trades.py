from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field


class FilterType(str, Enum):
    CASH = "CASH"
    TOKENS = "TOKENS"


class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


# ---------------------------------------------------------------------------
# Request
# ---------------------------------------------------------------------------

class TradesParams(BaseModel):
    limit: int | None = Field(default=100, ge=0, le=10000)
    offset: int | None = Field(default=0, ge=0, le=100000)
    takerOnly: bool | None = Field(default=True)
    filterType: FilterType | None = None   # must be paired with filterAmount
    filterAmount: float | None = Field(default=None, ge=0)  # must be paired with filterType
    market: list[str] | None = None        # condition IDs; mutually exclusive with eventId
    eventId: list[int] | None = Field(default=None)  # mutually exclusive with market
    user: str | None = Field(default=None, pattern=r"^0x[a-fA-F0-9]{40}$")
    side: Side | None = None


# ---------------------------------------------------------------------------
# Response
# ---------------------------------------------------------------------------

class Trade(BaseModel):
    proxyWallet: str | None = Field(default=None, pattern=r"^0x[a-fA-F0-9]{40}$")
    side: Side | None = None
    asset: str | None = None
    conditionId: str | None = Field(default=None, pattern=r"^0x[a-fA-F0-9]{64}$")
    size: float | None = None
    price: float | None = None
    timestamp: int | None = None
    title: str | None = None
    slug: str | None = None
    icon: str | None = None
    eventSlug: str | None = None
    outcome: str | None = None
    outcomeIndex: int | None = None
    name: str | None = None
    pseudonym: str | None = None
    bio: str | None = None
    profileImage: str | None = None
    profileImageOptimized: str | None = None
    transactionHash: str | None = None
