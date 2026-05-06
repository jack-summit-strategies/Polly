import requests

from ..contracts.data import Trade, TradesParams
from ..util.rate_limiter import RateLimiter

# Rate limits (per 10 seconds):
#   General             1,000 req
#   /trades               200 req
#   /positions            150 req
#   /closed-positions     150 req
#   /ok (health check)    100 req


class DataAPI:
    BASE_URL = "https://data-api.polymarket.com"

    #
    # Constructor
    #

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self._limiters = {
            "/trades": RateLimiter(max_calls=200, period=10),
        }

    #
    # Utilities
    #

    def _get(self, path: str, params: dict = None) -> dict | list:
        limiter = self._limiters.get(path)
        if limiter:
            limiter.acquire()
        url = f"{self.BASE_URL}{path}"
        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    #
    #   Endpoints
    #

    # /trades - Endpoint — Rate Limit => 200 req / 10s
    def get_trades(self, params: TradesParams | None = None) -> list[Trade]:
        raw_params = params.model_dump(exclude_none=True) if params else {}
        data = self._get("/trades", params=raw_params)
        return [Trade.model_validate(item) for item in data]
