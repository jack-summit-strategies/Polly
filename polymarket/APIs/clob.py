import requests

from ..contracts.clob import PriceHistoryParams, PriceHistory
from ..util.rate_limiter import RateLimiter

# Rate limits (per 10 seconds):
#   General                     9,000 req
#   GET balance allowance         200 req
#   UPDATE balance allowance       50 req


class ClobAPI:
    BASE_URL = "https://clob.polymarket.com"

    #
    # Constructor
    #

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self._limiters = {
            "/price-history": RateLimiter(max_calls=9000, period=10),
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

    # /price-history - Endpoint — Rate Limit => 9,000 req / 10s (general)
    def get_price_history(self, params: PriceHistoryParams) -> PriceHistory:
        raw_params = params.model_dump(exclude_none=True)
        data = self._get("/prices-history", params=raw_params)
        return PriceHistory.model_validate(data)

    def get_price_history_chunked(self, params: PriceHistoryParams) -> PriceHistory:
        SEVEN_DAYS = 7 * 24 * 60 * 60

        start = params.startTs
        end = params.endTs

        if start is None or end is None or (end - start) <= SEVEN_DAYS:
            return self.get_price_history(params)

        all_points: list = []
        chunk_start = start
        while chunk_start < end:
            chunk_end = min(chunk_start + SEVEN_DAYS, end)
            chunk_params = params.model_copy(update={"startTs": chunk_start, "endTs": chunk_end})
            result = self.get_price_history(chunk_params)
            all_points.extend(result.history)
            chunk_start = chunk_end

        return PriceHistory(history=all_points)
