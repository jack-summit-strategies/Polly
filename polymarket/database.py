import duckdb
import json
from datetime import datetime
from pathlib import Path


class WhaleDatabase:
    """DuckDB database for storing and analyzing Polymarket whale trading data."""

    def __init__(self, db_path: str = "whale_trades.duckdb"):
        """Initialize DuckDB connection.

        Args:
            db_path: Path to DuckDB file
        """
        self.db_path = db_path
        self.conn = duckdb.connect(db_path)
        self._init_tables()

    def _init_tables(self):
        """Create required tables if they don't exist."""

        # Trades table
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id VARCHAR PRIMARY KEY,
            timestamp BIGINT NOT NULL,
            condition_id VARCHAR NOT NULL,
            maker VARCHAR NOT NULL,
            taker VARCHAR NOT NULL,
            outcome VARCHAR,
            shares DOUBLE NOT NULL,
            price DOUBLE NOT NULL,
            fee DOUBLE,
            transaction_hash VARCHAR,
            source VARCHAR,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Whale wallets table
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS whale_wallets (
            wallet VARCHAR PRIMARY KEY,
            total_trades INTEGER DEFAULT 0,
            total_volume DOUBLE DEFAULT 0,
            avg_trade_size DOUBLE DEFAULT 0,
            win_rate DOUBLE DEFAULT 0,
            markets_traded INTEGER DEFAULT 0,
            first_trade_timestamp BIGINT,
            last_trade_timestamp BIGINT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Market analytics table
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS market_analytics (
            condition_id VARCHAR PRIMARY KEY,
            total_trades INTEGER DEFAULT 0,
            total_volume DOUBLE DEFAULT 0,
            unique_wallets INTEGER DEFAULT 0,
            whale_trades INTEGER DEFAULT 0,
            first_trade_timestamp BIGINT,
            last_trade_timestamp BIGINT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Live monitoring table
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS monitoring_sessions (
            session_id VARCHAR PRIMARY KEY,
            market_ids VARCHAR,
            wallet_addresses VARCHAR,
            status VARCHAR DEFAULT 'active',
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_time TIMESTAMP,
            trades_monitored INTEGER DEFAULT 0,
            whales_detected INTEGER DEFAULT 0
        )
        """)

    def insert_trade(self, trade: dict, source: str = "subgraph") -> bool:
        """Insert a trade record.

        Args:
            trade: Trade data dictionary
            source: Source of trade data (subgraph, api, etc.)

        Returns:
            True if inserted, False if already exists
        """
        try:
            self.conn.execute("""
            INSERT INTO trades (
                id, timestamp, condition_id, maker, taker,
                outcome, shares, price, fee, transaction_hash, source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                trade.get("id"),
                trade.get("timestamp"),
                trade.get("condition_id") or trade.get("condition"),
                trade.get("maker"),
                trade.get("taker"),
                trade.get("outcome"),
                float(trade.get("shares", 0)),
                float(trade.get("price", 0)),
                trade.get("fee"),
                trade.get("transaction_hash") or trade.get("transactionHash"),
                source
            ))
            return True
        except Exception:
            return False

    def insert_trades_batch(self, trades: list[dict], source: str = "subgraph") -> int:
        """Insert multiple trades efficiently.

        Args:
            trades: List of trade dictionaries
            source: Source of trade data

        Returns:
            Number of trades inserted
        """
        if not trades:
            return 0

        inserted = 0
        for trade in trades:
            if self.insert_trade(trade, source):
                inserted += 1

        return inserted

    def get_trades_by_wallet(self, wallet: str) -> list[dict]:
        """Retrieve all trades for a wallet.

        Args:
            wallet: Wallet address

        Returns:
            List of trade records
        """
        result = self.conn.execute("""
        SELECT * FROM trades
        WHERE maker = ? OR taker = ?
        ORDER BY timestamp DESC
        """, [wallet, wallet]).fetchall()

        return [dict(row) for row in result]

    def get_trades_by_market(self, condition_id: str) -> list[dict]:
        """Retrieve all trades for a market.

        Args:
            condition_id: Market condition ID

        Returns:
            List of trade records
        """
        result = self.conn.execute("""
        SELECT * FROM trades
        WHERE condition_id = ?
        ORDER BY timestamp DESC
        """, [condition_id]).fetchall()

        return [dict(row) for row in result]

    def get_whale_wallets(self, min_trades: int = 3, min_volume: float = 5000) -> list[dict]:
        """Retrieve wallets matching whale criteria.

        Args:
            min_trades: Minimum number of trades
            min_volume: Minimum total trade volume

        Returns:
            List of whale wallet records
        """
        result = self.conn.execute("""
        SELECT * FROM whale_wallets
        WHERE total_trades >= ? AND total_volume >= ?
        ORDER BY total_volume DESC
        """, [min_trades, min_volume]).fetchall()

        return [dict(row) for row in result]

    def update_whale_stats(self, wallet: str):
        """Calculate and update whale statistics for a wallet.

        Args:
            wallet: Wallet address
        """
        # Calculate stats
        stats = self.conn.execute("""
        SELECT
            COUNT(*) as total_trades,
            SUM(shares * price) as total_volume,
            AVG(shares * price) as avg_trade_size,
            MIN(timestamp) as first_trade,
            MAX(timestamp) as last_trade,
            COUNT(DISTINCT condition_id) as markets_traded
        FROM trades
        WHERE maker = ? OR taker = ?
        """, [wallet, wallet]).fetchone()

        if stats and stats[0] > 0:
            # Check if wallet exists
            exists = self.conn.execute(
                "SELECT 1 FROM whale_wallets WHERE wallet = ?",
                [wallet]
            ).fetchone()

            if exists:
                self.conn.execute("""
                UPDATE whale_wallets SET
                    total_trades = ?,
                    total_volume = ?,
                    avg_trade_size = ?,
                    first_trade_timestamp = ?,
                    last_trade_timestamp = ?,
                    markets_traded = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE wallet = ?
                """, [
                    stats[0], stats[1], stats[2], stats[3], stats[4], stats[5],
                    wallet
                ])
            else:
                self.conn.execute("""
                INSERT INTO whale_wallets
                (wallet, total_trades, total_volume, avg_trade_size,
                 first_trade_timestamp, last_trade_timestamp, markets_traded)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, [
                    wallet,
                    stats[0], stats[1], stats[2], stats[3], stats[4], stats[5]
                ])

    def update_market_analytics(self, condition_id: str):
        """Calculate and update analytics for a market.

        Args:
            condition_id: Market condition ID
        """
        # Get basic stats
        stats = self.conn.execute("""
        SELECT
            COUNT(*) as total_trades,
            SUM(shares * price) as total_volume,
            MIN(timestamp) as first_trade,
            MAX(timestamp) as last_trade
        FROM trades
        WHERE condition_id = ?
        """, [condition_id]).fetchone()

        if stats and stats[0] > 0:
            # Count unique wallets
            unique_wallets = self.conn.execute("""
            SELECT COUNT(DISTINCT wallet) FROM (
                SELECT DISTINCT maker as wallet FROM trades WHERE condition_id = ?
                UNION
                SELECT DISTINCT taker as wallet FROM trades WHERE condition_id = ?
            )
            """, [condition_id, condition_id]).fetchone()[0]

            # Count whale trades
            whale_count = self.conn.execute("""
            SELECT COUNT(*) FROM trades
            WHERE condition_id = ? AND (shares * price) >= 5000
            """, [condition_id]).fetchone()[0]

            # Check if market exists
            exists = self.conn.execute(
                "SELECT 1 FROM market_analytics WHERE condition_id = ?",
                [condition_id]
            ).fetchone()

            if exists:
                self.conn.execute("""
                UPDATE market_analytics SET
                    total_trades = ?,
                    total_volume = ?,
                    unique_wallets = ?,
                    whale_trades = ?,
                    first_trade_timestamp = ?,
                    last_trade_timestamp = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE condition_id = ?
                """, [
                    stats[0], stats[1], unique_wallets, whale_count, stats[2], stats[3],
                    condition_id
                ])
            else:
                self.conn.execute("""
                INSERT INTO market_analytics
                (condition_id, total_trades, total_volume, unique_wallets,
                 whale_trades, first_trade_timestamp, last_trade_timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, [
                    condition_id,
                    stats[0], stats[1], unique_wallets, whale_count, stats[2], stats[3]
                ])

    def get_market_analytics(self, condition_id: str) -> dict:
        """Get analytics for a market.

        Args:
            condition_id: Market condition ID

        Returns:
            Market analytics record
        """
        result = self.conn.execute(
            "SELECT * FROM market_analytics WHERE condition_id = ?",
            [condition_id]
        ).fetchone()

        return dict(result) if result else None

    def get_recent_trades(self, limit: int = 100) -> list[dict]:
        """Get most recent trades across all markets.

        Args:
            limit: Number of trades to return

        Returns:
            List of recent trade records
        """
        result = self.conn.execute("""
        SELECT * FROM trades
        ORDER BY timestamp DESC
        LIMIT ?
        """, [limit]).fetchall()

        return [dict(row) for row in result]

    def get_market_whale_concentration(self, condition_id: str) -> dict:
        """Analyze whale concentration in a market.

        Args:
            condition_id: Market condition ID

        Returns:
            Dictionary with concentration metrics
        """
        result = self.conn.execute("""
        SELECT
            COUNT(DISTINCT maker) as total_traders,
            SUM(shares * price) as total_volume,
            PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY (shares * price)) as p95_trade_size,
            PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY (shares * price)) as p99_trade_size,
            MAX(shares * price) as largest_trade
        FROM trades
        WHERE condition_id = ?
        """, [condition_id]).fetchone()

        if result:
            return {
                "total_traders": result[0],
                "total_volume": result[1],
                "p95_trade_size": result[2],
                "p99_trade_size": result[3],
                "largest_trade": result[4]
            }
        return None

    def get_wallet_win_rate(self, wallet: str) -> dict:
        """Calculate win rate and profitability for a wallet.

        Args:
            wallet: Wallet address

        Returns:
            Dictionary with win metrics
        """
        result = self.conn.execute("""
        SELECT
            outcome,
            COUNT(*) as count,
            AVG(price) as avg_price,
            SUM(shares) as total_shares
        FROM trades
        WHERE maker = ? OR taker = ?
        GROUP BY outcome
        """, [wallet, wallet]).fetchall()

        if result:
            return {outcome: {"count": count, "avg_price": price, "shares": shares}
                    for outcome, count, price, shares in result}
        return None

    def export_to_json(self, filename: str):
        """Export all trades to JSON file.

        Args:
            filename: Output JSON file path
        """
        result = self.conn.execute("SELECT * FROM trades ORDER BY timestamp DESC").fetchall()
        trades_list = [dict(row) for row in result]

        with open(filename, "w") as f:
            json.dump(trades_list, f, indent=2, default=str)

    def export_market_report(self, condition_id: str, filename: str):
        """Export detailed market analysis report.

        Args:
            condition_id: Market condition ID
            filename: Output JSON file path
        """
        analytics = self.get_market_analytics(condition_id)
        trades = self.get_trades_by_market(condition_id)

        report = {
            "market": condition_id,
            "analytics": analytics,
            "trades_count": len(trades),
            "sample_trades": trades[:100]
        }

        with open(filename, "w") as f:
            json.dump(report, f, indent=2, default=str)

    def close(self):
        """Close database connection."""
        self.conn.close()

    def get_summary_stats(self) -> dict:
        """Get overall database statistics.

        Returns:
            Dictionary with summary statistics
        """
        result = self.conn.execute("""
        SELECT
            (SELECT COUNT(*) FROM trades) as total_trades,
            (SELECT COUNT(DISTINCT condition_id) FROM trades) as markets,
            (SELECT COUNT(*) FROM whale_wallets) as whale_wallets,
            (SELECT SUM(total_volume) FROM market_analytics) as total_market_volume
        """).fetchone()

        return {
            "total_trades": result[0],
            "markets_tracked": result[1],
            "whale_wallets": result[2],
            "total_market_volume": result[3]
        }
