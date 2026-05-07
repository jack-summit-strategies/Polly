import requests

from ..contracts.gamma import Event, EventsParams, Profile, ProfileParams, Tag
from ..util.rate_limiter import RateLimiter

# Rate limits (per 10 seconds):
#   General             4,000 req
#   /events               500 req
#   /markets              300 req
#   /markets + /events    900 req  (combined listing)
#   /comments             200 req
#   /tags                 200 req
#   /public-search        350 req


class GammaAPI:
    BASE_URL = "https://gamma-api.polymarket.com"

    #
    # Constructor
    #

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self._limiters = {
            "/events": RateLimiter(max_calls=500, period=10),
            "/tags": RateLimiter(max_calls=200, period=10),
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

    # /events
    def get_events(self, params: EventsParams | None = None) -> list[Event]:
        raw_params = params.model_dump(exclude_none=True) if params else {}
        data = self._get("/events", params=raw_params)
        return [Event.model_validate(item) for item in data]

    # /public-profile
    def get_profile(self, params: ProfileParams) -> Profile:
        raw_params = params.model_dump(exclude_none=True)
        data = self._get("/public-profile", params=raw_params)
        return Profile.model_validate(data)

    # /tags
    def get_tags(self) -> list[Tag]:
        data = self._get("/tags")
        return [Tag.model_validate(item) for item in data]
