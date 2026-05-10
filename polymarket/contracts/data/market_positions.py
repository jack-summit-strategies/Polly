from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field


class PositionStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    ALL = "ALL"


class PositionSortBy(str, Enum):
    TOKENS = "TOKENS"
    CASH_PNL = "CASH_PNL"
    REALIZED_PNL = "REALIZED_PNL"
    TOTAL_PNL = "TOTAL_PNL"


class SortDirection(str, Enum):
    ASC = "ASC"
    DESC = "DESC"


# ---------------------------------------------------------------------------
# Request
# ---------------------------------------------------------------------------

class MarketPositionsParams(BaseModel):
    market: str = Field(pattern=r"^0x[a-fA-F0-9]{64}$")
    user: str | None = Field(default=None, pattern=r"^0x[a-fA-F0-9]{40}$")
    status: PositionStatus | None = Field(default=PositionStatus.ALL)
    sortBy: PositionSortBy | None = Field(default=PositionSortBy.TOTAL_PNL)
    sortDirection: SortDirection | None = Field(default=SortDirection.DESC)
    limit: int | None = Field(default=50, ge=0, le=500)
    offset: int | None = Field(default=0, ge=0, le=10000)


# ---------------------------------------------------------------------------
# Response
# ---------------------------------------------------------------------------

class Position(BaseModel):
    proxyWallet: str | None = Field(default=None, pattern=r"^0x[a-fA-F0-9]{40}$")
    name: str | None = None
    profileImage: str | None = None
    verified: bool | None = None
    asset: str | None = None
    conditionId: str | None = Field(default=None, pattern=r"^0x[a-fA-F0-9]{64}$")
    avgPrice: float | None = None
    size: float | None = None
    currPrice: float | None = None
    currentValue: float | None = None
    cashPnl: float | None = None
    totalBought: float | None = None
    realizedPnl: float | None = None
    totalPnl: float | None = None
    outcome: str | None = None
    outcomeIndex: int | None = None


class MarketPositionGroup(BaseModel):
    token: str | None = None
    positions: list[Position] = Field(default_factory=list)
