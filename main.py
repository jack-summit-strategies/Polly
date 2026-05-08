import sys
sys.stdout.reconfigure(encoding="utf-8")

import json
from datetime import datetime, timedelta
from collections import defaultdict
from polymarket import Polymarket
from polymarket.subgraph import PolymarketSubgraph
from polymarket.database import WhaleDatabase
from polymarket.contracts.gamma import EventsParams
from polymarket.contracts.data import TradesParams, Side, FilterType


pm = Polymarket()
db = WhaleDatabase(db_path="whale_trades.db")


# ============================================================================
# SUBGRAPH FUNCTIONS - HISTORICAL DATA
# ============================================================================

def fetch_market_history_subgraph(condition_id: str, api_key: str = None):
    """Fetch complete trade history for a market from subgraph.

    Args:
        condition_id: Market condition ID
        api_key: The Graph API key (optional, uses public endpoint if None)
    """
    print("\n" + "="*80)
    print(f"FETCHING MARKET HISTORY FROM SUBGRAPH: {condition_id[:20]}...")
    print("="*80)

    subgraph = PolymarketSubgraph(api_key=api_key)

    skip = 0
    batch_size = 1000
    total_inserted = 0
    all_trades = []

    try:
        while True:
            print(f"Fetching batch starting at offset {skip}...")
            trades = subgraph.get_market_trades(condition_id, first=batch_size, skip=skip)

            if not trades:
                print("No more trades found")
                break

            # Add condition_id to each trade
            for trade in trades:
                trade["condition_id"] = condition_id

            all_trades.extend(trades)

            # Insert into database
            inserted = db.insert_trades_batch(trades, source="subgraph")
            total_inserted += inserted
            print(f"  Inserted {inserted} trades (total: {total_inserted})")

            if len(trades) < batch_size:
                break

            skip += batch_size

        db.update_market_analytics(condition_id)
        print(f"\nTotal trades fetched and stored: {total_inserted}")

    except Exception as e:
        print(f"Error fetching subgraph data: {e}")
        print("Note: API key may be required. Visit https://thegraph.com/studio to get one.")


def fetch_wallet_history_subgraph(wallet: str, api_key: str = None):
    """Fetch all trades for a wallet from subgraph.

    Args:
        wallet: Wallet address
        api_key: The Graph API key
    """
    print("\n" + "="*80)
    print(f"FETCHING WALLET HISTORY FROM SUBGRAPH: {wallet}")
    print("="*80)

    subgraph = PolymarketSubgraph(api_key=api_key)

    try:
        trades = subgraph.get_wallet_trades(wallet, first=1000)
        print(f"Found {len(trades)} trades for wallet\n")

        for trade in trades[:10]:
            side = "MAKER" if trade.get("maker") == wallet else "TAKER"
            shares = trade.get("shares", 0)
            price = trade.get("price", 0)
            value = shares * price

            dt = datetime.fromtimestamp(trade.get("timestamp", 0))
            print(f"{side} {shares} shares @ {price} (${value:,.2f})")
            print(f"  Outcome: {trade.get('outcome')}")
            print(f"  Time: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
            print()

        # Insert into database
        inserted = db.insert_trades_batch(trades, source="subgraph")
        print(f"Stored {inserted} trades in database")

        db.update_whale_stats(wallet)

    except Exception as e:
        print(f"Error fetching wallet data: {e}")


def get_large_trades_subgraph(min_shares: int = 10000, api_key: str = None):
    """Fetch whale trades (large sizes) from subgraph.

    Args:
        min_shares: Minimum trade size
        api_key: The Graph API key
    """
    print("\n" + "="*80)
    print(f"WHALE TRADES FROM SUBGRAPH (min {min_shares} shares)")
    print("="*80)

    subgraph = PolymarketSubgraph(api_key=api_key)

    try:
        trades = subgraph.get_large_trades(min_shares=min_shares, first=1000)
        print(f"Found {len(trades)} large trades\n")

        # Group by wallet
        by_wallet = defaultdict(list)
        for trade in trades:
            maker = trade.get("maker")
            if maker:
                by_wallet[maker].append(trade)

        for wallet, wallet_trades in sorted(by_wallet.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
            total_volume = sum(t.get("shares", 0) * t.get("price", 0) for t in wallet_trades)
            print(f"{wallet[:10]}...{wallet[-4:]}")
            print(f"  Trades: {len(wallet_trades)}")
            print(f"  Total Volume: ${total_volume:,.2f}")
            print()

        # Store in database
        inserted = db.insert_trades_batch(trades, source="subgraph")
        print(f"Stored {inserted} trades in database")

    except Exception as e:
        print(f"Error fetching whale trades: {e}")


# ============================================================================
# DATABASE ANALYSIS FUNCTIONS
# ============================================================================

def analyze_stored_whales(min_trades: int = 3):
    """Analyze whale wallets from database.

    Args:
        min_trades: Minimum trades to qualify as whale
    """
    print("\n" + "="*80)
    print("STORED WHALE WALLETS ANALYSIS")
    print("="*80)

    whales = db.get_whale_wallets(min_trades=min_trades, min_volume=0)
    print(f"Found {len(whales)} whale wallets\n")

    for whale in whales[:20]:
        print(f"{whale['wallet'][:10]}...{whale['wallet'][-4:]}")
        print(f"  Total Trades: {whale.get('total_trades', 0)}")
        print(f"  Total Volume: ${whale.get('total_volume', 0):,.2f}")
        print(f"  Avg Trade: ${whale.get('avg_trade_size', 0):,.2f}")
        print(f"  Markets: {whale.get('markets_traded', 0)}")
        print()


def get_market_summary(condition_id: str):
    """Get summary statistics for a market.

    Args:
        condition_id: Market condition ID
    """
    print("\n" + "="*80)
    print(f"MARKET SUMMARY: {condition_id[:20]}...")
    print("="*80)

    analytics = db.get_market_analytics(condition_id)

    if analytics:
        print(f"Total Trades: {analytics.get('total_trades', 0)}")
        print(f"Total Volume: ${analytics.get('total_volume', 0):,.2f}")
        print(f"Unique Wallets: {analytics.get('unique_wallets', 0)}")
        print(f"Whale Trades (5k+): {analytics.get('whale_trades', 0)}")

        if analytics.get('first_trade_timestamp'):
            start = datetime.fromtimestamp(analytics['first_trade_timestamp'])
            end = datetime.fromtimestamp(analytics['last_trade_timestamp'])
            print(f"Trading Period: {start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}")
    else:
        print("No analytics found for this market")


# ============================================================================
# TAG DISCOVERY (FROM EXISTING CODE)
# ============================================================================

def discover_tags():
    """Fetch and display all available tags for filtering events."""
    print("\n" + "="*80)
    print("AVAILABLE TAGS")
    print("="*80)

    tags = pm.gamma.get_tags()
    print(f"Found {len(tags)} tags\n")

    for tag in sorted(tags, key=lambda t: t.label or '')[:50]:
        print(f"ID: {tag.id:>6} | Label: {tag.label:30} | Slug: {tag.slug}")


# ============================================================================
# SETUP AND CONFIGURATION
# ============================================================================

def setup_subgraph_monitoring(api_key: str = None):
    """Interactive setup for subgraph monitoring.

    Args:
        api_key: The Graph API key (optional)
    """
    print("\n" + "="*80)
    print("SUBGRAPH MONITORING SETUP")
    print("="*80)

    if not api_key:
        print("\nTo use the Polymarket subgraph:")
        print("1. Go to https://thegraph.com/studio")
        print("2. Connect your wallet")
        print("3. Create an API key")
        print("4. Use it with these functions")
        print("\nFree tier: 100k queries/month\n")
        api_key = input("Enter your API key (or press Enter to skip): ").strip()

    return api_key


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("\nPolymarket Whale Tracking System")
    print("With Subgraph Integration & Database Storage\n")

    # Step 1: Discover tags
    discover_tags()

    # Step 2: Get a political event and its market
    print("\n" + "="*80)
    print("FETCHING POLITICAL EVENTS FOR TESTING")
    print("="*80)

    params = EventsParams(
        limit=3,
        tag_id=100344,
        order="volume",
        ascending=False,
    )

    events = pm.gamma.get_events(params)

    if events and events[0].markets:
        event = events[0]
        market = event.markets[0]

        print(f"\nEvent: {event.title}")
        print(f"Market: {market.question}")
        print(f"Condition ID: {market.conditionId}\n")

        # Step 3: Fetch historical data from subgraph
        if market.conditionId:
            api_key = setup_subgraph_monitoring()
            fetch_market_history_subgraph(market.conditionId, api_key=api_key)

            # Step 4: Analyze stored data
            get_market_summary(market.conditionId)

            # Step 5: Find whales in stored data
            analyze_stored_whales()

    print("\n" + "="*80)
    print("Analysis complete")
    print("Database saved to: whale_trades.db")
    print("="*80)

    db.close()
