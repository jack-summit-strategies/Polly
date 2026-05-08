import sys
sys.stdout.reconfigure(encoding="utf-8")

from polymarket import Polymarket
from polymarket.contracts.gamma import EventsParams
from polymarket.contracts.data import TradesParams

pm = Polymarket()

params = EventsParams(
    limit=1,
    offset=0,
    order="endDate",
    ascending=False,
    tag_id=100265,
    closed=True,
    start_date_min="2025-01-01T00:00:00Z",
    end_date_max="2026-01-01T00:00:00Z",
)

events = pm.gamma.get_events(params)

data_params = TradesParams(
    limit=5,
    offset=0,
    market=[events[0].markets[0].conditionId]
)

