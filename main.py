import sys
sys.stdout.reconfigure(encoding="utf-8")

import json
from datetime import datetime, timedelta
from collections import defaultdict
from polymarket import Polymarket
from polymarket.contracts.gamma import EventsParams
from polymarket.contracts.data import TradesParams, Side, FilterType


pm = Polymarket()


# ============================================================================
# TAG DISCOVERY
# ============================================================================

def discover_tags():
    """Fetch and display all available tags for filtering events."""
    print("\n" + "="*80)
    print("AVAILABLE TAGS")
    print("="*80)

    tags = pm.gamma.get_tags()
    print(f"Found {len(tags)} tags\n")

    for tag in sorted(tags, key=lambda t: t.label or ''):
        print(f"ID: {tag.id:>6} | Label: {tag.label:30} | Slug: {tag.slug}")


# ============================================================================
# EVENT FETCHING
# ============================================================================

def get_political_events(tag_ids: list[int], limit: int = 10, active_only: bool = True):
    """Fetch political events filtered by tag IDs."""
    print("\n" + "="*80)
    print("POLITICAL EVENTS")
    print("="*80)

    all_events = []
    for tag_id in tag_ids:
        params = EventsParams(
            limit=limit,
            offset=0,
            tag_id=tag_id,
            active=active_only if active_only else None,
            order="volume",
            ascending=False,
        )
        events = pm.gamma.get_events(params)
        all_events.extend(events)

    print(f"Found {len(all_events)} events across {len(tag_ids)} political tags\n")

    for event in all_events[:limit]:
        market_count = len(event.markets) if event.markets else 0
        print(f"{event.title}")
        print(f"  Ticker: {event.ticker}")
        print(f"  Status: {'Closed' if event.closed else 'Active'}")
        print(f"  Volume: ${event.volume:,.0f}" if event.volume else "  Volume: N/A")
        print(f"  Markets: {market_count}")
        print()


def get_sports_events(tag_ids: list[int], limit: int = 10, active_only: bool = True):
    """Fetch sports events filtered by tag IDs."""
    print("\n" + "="*80)
    print("SPORTS EVENTS")
    print("="*80)

    all_events = []
    for tag_id in tag_ids:
        params = EventsParams(
            limit=limit,
            offset=0,
            tag_id=tag_id,
            active=active_only if active_only else None,
            order="volume",
            ascending=False,
        )
        events = pm.gamma.get_events(params)
        all_events.extend(events)

    print(f"Found {len(all_events)} events across {len(tag_ids)} sports tags\n")

    for event in all_events[:limit]:
        market_count = len(event.markets) if event.markets else 0
        print(f"{event.title}")
        print(f"  Ticker: {event.ticker}")
        print(f"  Status: {'Closed' if event.closed else 'Active'}")
        print(f"  Volume: ${event.volume:,.0f}" if event.volume else "  Volume: N/A")
        print(f"  Markets: {market_count}")
        print()


# ============================================================================
# TRADE PAGINATION & WHALE DETECTION
# ============================================================================

def paginate_all_trades(market_ids: list[str], min_cash: float = None, page_size: int = 100):
    """Paginate through ALL trades for given markets, yielding Trade objects."""
    offset = 0
    total_fetched = 0

    while True:
        params = TradesParams(
            limit=page_size,
            offset=offset,
            market=market_ids,
            takerOnly=False,
            filterType=FilterType.CASH if min_cash else None,
            filterAmount=min_cash if min_cash else None,
        )

        trades = pm.data.get_trades(params)

        if not trades:
            break

        for trade in trades:
            yield trade
            total_fetched += 1

        if len(trades) < page_size:
            break

        offset += page_size

    print(f"(Fetched {total_fetched} trades total)")


def scan_whale_trades(event, min_cash: float = 5000):
    """Scan all trades in an event's markets for whale activity (trades >= min_cash)."""
    print("\n" + "="*80)
    print(f"WHALE TRADES: {event.title}")
    print("="*80)

    if not event.markets:
        print("No markets found for this event")
        return

    market_ids = [m.conditionId for m in event.markets if m.conditionId]

    if not market_ids:
        print("No valid market IDs found")
        return

    print(f"Scanning {len(market_ids)} markets for trades >= ${min_cash}\n")

    whale_trades = defaultdict(list)
    total_trades = 0

    for trade in paginate_all_trades(market_ids, min_cash=min_cash):
        total_trades += 1
        if trade.proxyWallet:
            whale_trades[trade.proxyWallet].append(trade)

    print(f"Found {sum(len(v) for v in whale_trades.values())} whale trades from {len(whale_trades)} unique wallets\n")

    # Sort wallets by number of whale trades
    for wallet, trades in sorted(whale_trades.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
        total_size = sum(t.size for t in trades if t.size)
        total_value = sum(t.size * t.price for t in trades if t.size and t.price)

        print(f"{wallet[:10]}...{wallet[-4:]}")
        print(f"  Trades: {len(trades)}")
        print(f"  Total Size: {total_size:,.2f}")
        print(f"  Total Value: ${total_value:,.2f}")
        print(f"  Wins: {sum(1 for t in trades if t.outcome and t.outcome.lower() in ['yes', 'win'])}")
        print()


# ============================================================================
# WALLET TRACKING
# ============================================================================

def track_wallet(address: str, limit: int = 100):
    """Fetch full trade history for a specific wallet address."""
    print("\n" + "="*80)
    print(f"WALLET HISTORY: {address}")
    print("="*80)

    params = TradesParams(
        limit=limit,
        offset=0,
        user=address,
    )

    trades = pm.data.get_trades(params)

    print(f"Found {len(trades)} trades\n")

    if not trades:
        print("No trades found")
        return

    buy_trades = [t for t in trades if t.side == Side.BUY]
    sell_trades = [t for t in trades if t.side == Side.SELL]
    total_size = sum(t.size for t in trades if t.size)
    total_value = sum(t.size * t.price for t in trades if t.size and t.price)

    print("Summary:")
    print(f"  Total Trades: {len(trades)}")
    print(f"  Buys: {len(buy_trades)}")
    print(f"  Sells: {len(sell_trades)}")
    print(f"  Total Size: {total_size:,.2f}")
    print(f"  Total Value: ${total_value:,.2f}")
    print()

    print("Recent Trades (first 10):")
    for trade in trades[:10]:
        side = trade.side.value if trade.side else "N/A"
        print(f"  {side} {trade.size} of {trade.outcome} @ ${trade.price}")
        print(f"    Market: {trade.title}")
        if trade.timestamp:
            dt = datetime.fromtimestamp(trade.timestamp)
            print(f"    Time: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
        print()


def find_whale_wallets(events: list, min_cash: float = 5000, min_trades: int = 2):
    """Identify wallets that consistently make large trades across events."""
    print("\n" + "="*80)
    print(f"WHALE WALLET LEADERBOARD (min ${min_cash} per trade)")
    print("="*80)

    wallet_stats = defaultdict(lambda: {
        "events_traded": set(),
        "total_trades": 0,
        "total_value": 0,
        "markets": set(),
    })

    total_events_scanned = 0
    total_whales_found = 0

    for event in events:
        if not event.markets:
            continue

        total_events_scanned += 1
        market_ids = [m.conditionId for m in event.markets if m.conditionId]

        if not market_ids:
            continue

        for trade in paginate_all_trades(market_ids, min_cash=min_cash):
            if trade.proxyWallet:
                total_whales_found += 1
                wallet_stats[trade.proxyWallet]["events_traded"].add(event.id)
                wallet_stats[trade.proxyWallet]["total_trades"] += 1
                if trade.size and trade.price:
                    wallet_stats[trade.proxyWallet]["total_value"] += trade.size * trade.price
                if trade.conditionId:
                    wallet_stats[trade.proxyWallet]["markets"].add(trade.conditionId)

    print(f"Scanned {total_events_scanned} events")
    print(f"Found {total_whales_found} whale trades\n")

    # Filter to wallets active in multiple events
    consistent_whales = {
        w: s for w, s in wallet_stats.items()
        if len(s["events_traded"]) >= min_trades
    }

    print(f"Wallets active in {min_trades}+ events: {len(consistent_whales)}\n")

    # Rank by number of events traded
    for wallet, stats in sorted(
        consistent_whales.items(),
        key=lambda x: len(x[1]["events_traded"]),
        reverse=True
    )[:20]:
        print(f"{wallet[:10]}...{wallet[-4:]}")
        print(f"  Events Traded: {len(stats['events_traded'])}")
        print(f"  Total Whale Trades: {stats['total_trades']}")
        print(f"  Total Value: ${stats['total_value']:,.2f}")
        print(f"  Markets: {len(stats['markets'])}")
        print()


# ============================================================================
# INSIDER DETECTION
# ============================================================================

def analyze_market_timeline(event):
    """Detect large trades early in a market's lifetime (potential insider activity)."""
    print("\n" + "="*80)
    print(f"EARLY WHALE DETECTION: {event.title}")
    print("="*80)

    if not event.markets:
        print("No markets found")
        return

    for market in event.markets[:3]:
        if not market.conditionId or not market.startDate or not market.endDate:
            continue

        print(f"\nMarket: {market.question}")
        print(f"  Start: {market.startDate}")
        print(f"  End: {market.endDate}")

        # Calculate first 10% of market lifetime
        duration = market.endDate - market.startDate
        early_cutoff = market.startDate + (duration * 0.1)

        params = TradesParams(
            limit=1000,
            offset=0,
            market=[market.conditionId],
            takerOnly=False,
        )

        trades = pm.data.get_trades(params)

        # Filter to early large trades
        early_large = []
        for trade in trades:
            if trade.timestamp:
                trade_time = datetime.fromtimestamp(trade.timestamp)
                if trade_time <= early_cutoff and trade.size and trade.price:
                    trade_value = trade.size * trade.price
                    if trade_value >= 5000:
                        early_large.append((trade, trade_time, trade_value))

        if early_large:
            print(f"  Found {len(early_large)} large trades in first 10% of market lifetime:")
            for trade, trade_time, value in sorted(early_large, key=lambda x: x[2], reverse=True)[:5]:
                print(f"    {trade_time.strftime('%Y-%m-%d %H:%M')}: {trade.side.value} {trade.size} @ ${trade.price} (${value:,.0f})")
                print(f"      Outcome: {trade.outcome}")
                print(f"      Wallet: {trade.proxyWallet[:10] if trade.proxyWallet else 'N/A'}...")
        else:
            print("  No early large trades detected")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Step 1: Discover available tags
    discover_tags()

    # Step 2: Example - Fetch political events (using known political tag IDs)
    political_tag_ids = [100344]
    get_political_events(political_tag_ids, limit=3)

    # Step 3: Example - Fetch sports events (using known sports tag IDs)
    sports_tag_ids = [1234, 1512, 1188, 102934]
    get_sports_events(sports_tag_ids, limit=3)

    # Step 4: Scan for whale activity in recent political events
    print("\n" + "="*80)
    print("FETCHING EVENTS FOR WHALE SCANNING")
    print("="*80)

    params = EventsParams(
        limit=5,
        offset=0,
        tag_id=100344,
        active=True,
        order="volume",
        ascending=False,
    )

    political_events = pm.gamma.get_events(params)

    for event in political_events[:2]:
        scan_whale_trades(event, min_cash=5000)
        analyze_market_timeline(event)

    # Step 5: Find consistent whale wallets across events
    if len(political_events) >= 3:
        find_whale_wallets(political_events, min_cash=5000, min_trades=2)

    print("\n" + "="*80)
    print("Analysis complete")
    print("="*80)
