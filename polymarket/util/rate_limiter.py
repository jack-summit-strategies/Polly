import time
from collections import deque


class RateLimiter:
    def __init__(self, max_calls: int, period: float):
        self.max_calls = max_calls
        self.period = period
        self._calls: deque[float] = deque()

    def acquire(self) -> None:
        now = time.monotonic()
        while self._calls and self._calls[0] <= now - self.period:
            self._calls.popleft()

        if len(self._calls) >= self.max_calls:
            sleep_for = self.period - (now - self._calls[0])
            if sleep_for > 0:
                time.sleep(sleep_for)
            now = time.monotonic()
            while self._calls and self._calls[0] <= now - self.period:
                self._calls.popleft()

        self._calls.append(time.monotonic())
