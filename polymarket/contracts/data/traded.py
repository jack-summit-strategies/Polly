from __future__ import annotations

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Request
# ---------------------------------------------------------------------------

class TradedParams(BaseModel):
    user: str = Field(pattern=r"^0x[a-fA-F0-9]{40}$")


# ---------------------------------------------------------------------------
# Response
# ---------------------------------------------------------------------------

class Traded(BaseModel):
    user: str | None = Field(default=None, pattern=r"^0x[a-fA-F0-9]{40}$")
    traded: float | None = None
