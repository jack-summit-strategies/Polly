from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Request
# ---------------------------------------------------------------------------

class ProfileParams(BaseModel):
    address: str = Field(pattern=r"^0x[a-fA-F0-9]{40}$")


# ---------------------------------------------------------------------------
# Response
# ---------------------------------------------------------------------------

class Profile(BaseModel):
    createdAt: datetime | None = None
    proxyWallet: str | None = None
    profileImage: str | None = None
    displayUsernamePublic: bool | None = None
    bio: str | None = None
    pseudonym: str | None = None
    name: str | None = None
    users: list[ProfileUser] | None = None
    xUsername: str | None = None
    verifiedBadge: bool | None = None



class ProfileUser(BaseModel):
    id: str | None = None
    creator: bool | None = None
    mod: bool | None = None
