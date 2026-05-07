# Polly - Polymarket Whale Tracking System

A comprehensive system for tracking whale trades and detecting potential insider activity on Polymarket using The Graph subgraph integration and DuckDB analytics.

## Features

- **Unlimited Historical Data**: Query complete trade history via Polymarket subgraph (no API limits)
- **Whale Detection**: Identify large trades ($5,000+) and suspicious wallet patterns
- **Database Analytics**: DuckDB-backed analysis for whale concentration and win rates
- **Real-time Monitoring**: Track whale activity as it happens
- **Market Analysis**: Event-level and market-level analytics

## Architecture

### Components

1. **Polymarket API Client** (`polymarket/`)
   - `polymarket.py` - Main facade
   - `APIs/` - Gamma, Data, and CLOB API wrappers
   - `contracts/` - Data models for events, trades, prices
   - `subgraph.py` - GraphQL client for The Graph subgraph

2. **Database** (`polymarket/database.py`)
   - DuckDB-based storage for trades and analytics
   - Whale wallet tracking
   - Market concentration metrics
   - Historical data persistence

3. **Scripts** (`main.py`)
   - Tag discovery
   - Event fetching (political, sports)
   - Whale trade detection
   - Historical data import from subgraph
   - Analytics and reporting

## Installation

```bash
# Clone the repository
git clone https://github.com/ClaytonM556/Polly.git
cd Polly

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install package with dependencies
pip install -e .
```

## Getting Started

### 1. Get The Graph API Key (Optional but Recommended)

Visit [thegraph.com/studio](https://thegraph.com/studio) to create a free API key:
- Free tier: 100k queries/month
- Provides access to full Polymarket subgraph without rate limits

### 2. Run Whale Tracking

```python
from polymarket import Polymarket
from polymarket.subgraph import PolymarketSubgraph
from polymarket.database import WhaleDatabase

# Initialize
pm = Polymarket()
db = WhaleDatabase(db_path="whale_trades.duckdb")
subgraph = PolymarketSubgraph(api_key="YOUR_API_KEY")

# Get events
events = pm.gamma.get_events(tag_id=100344)

# Fetch historical trades
trades = subgraph.get_market_trades(condition_id=events[0].markets[0].conditionId)

# Store in database
db.insert_trades_batch(trades)

# Analyze whales
whales = db.get_whale_wallets(min_trades=3, min_volume=5000)
for whale in whales:
    print(f"Wallet: {whale['wallet']}")
    print(f"  Trades: {whale['total_trades']}")
    print(f"  Volume: ${whale['total_volume']:,.2f}")
```

### 3. Run Main Script

```bash
python main.py
```

This will:
1. Display available event tags
2. Fetch political events
3. Query subgraph for historical trades
4. Store trades in DuckDB
5. Analyze whale wallets
6. Generate market summary statistics

## Database

### Tables

- **trades** - Individual trade records with timestamp, maker, taker, price, size
- **whale_wallets** - Aggregated statistics for identified whale wallets
- **market_analytics** - Per-market statistics and whale concentration
- **monitoring_sessions** - Live monitoring session tracking

### Queries

```python
# Get all trades for a market
trades = db.get_trades_by_market(condition_id)

# Find whale wallets
whales = db.get_whale_wallets(min_trades=3, min_volume=5000)

# Get market whale concentration
concentration = db.get_market_whale_concentration(condition_id)

# Export data
db.export_to_json("trades.json")
db.export_market_report(condition_id, "market_report.json")
```

## Whale Detection Criteria

Default threshold: **$5,000+ per trade**

Whale wallets are identified by:
- Multiple large trades (3+)
- High total trading volume
- Activity across multiple markets
- Early trades in market lifetime (potential insider activity)

## Data Sources

1. **Polymarket Gamma API** - Event and market metadata
2. **Polymarket Data API** - Recent trade data (last 3000 trades)
3. **Polymarket Subgraph** - Complete historical trades (via The Graph)
4. **CLOB API** - Price history and order book data

## Rate Limits

- Gamma API: 500 req/10s for `/events`
- Data API: 200 req/10s for `/trades`
- The Graph: 100k queries/month (free tier)

## Next Steps

- [ ] Live monitoring service
- [ ] Wallet win-rate analysis
- [ ] Temporal pattern detection
- [ ] Cross-market whale tracking
- [ ] Alert system for suspicious activity

## Contributing

This project tracks whale trading activity for research and analysis purposes.

## License

MIT
