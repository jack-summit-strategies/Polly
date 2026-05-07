import sqlite3
import json
from datetime import datetime
from pathlib import Path


class WhaleDatabase:
    """SQLite database for storing Polymarket whale trading data."""

    def __init__(self, db_path: str = "whale_trades.db"):
        """Initialize database connection.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_tables()

    def _init_tables(self):
        """Create required tables if they don't exist."""
        cursor = self.conn.cursor()

        # Trades table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id TEXT PRIMARY KEY,
            timestamp INTEGER NOT NULL,
            condition_id TEXT NOT NULL,
            maker TEXT NOT NULL,
            taker TEXT NOT NULL,
            outcome TEXT,
            shares REAL NOT NULL,
            price REAL NOT NULL,
            fee REAL,
            transaction_hash TEXT,
            source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(transaction_hash, condition_id)
        )
        """)

        # Whale wallets table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS whale_wallets (
            wallet TEXT PRIMARY KEY,
            total_trades INTEGER DEFAULT 0,
            total_volume REAL DEFAULT 0,
            avg_trade_size REAL DEFAULT 0,
            win_rate REAL DEFAULT 0,
            markets_traded INTEGER DEFAULT 0,
            first_trade_timestamp INTEGER,
            last_trade_timestamp INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Market analytics table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS market_analytics (
            condition_id TEXT PRIMARY KEY,
            total_trades INTEGER DEFAULT 0,
            total_volume REAL DEFAULT 0,
            unique_wallets INTEGER DEFAULT 0,
            whale_trades INTEGER DEFAULT 0,
            first_trade_timestamp INTEGER,
            last_trade_timestamp INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Live monitoring table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS monitoring_sessions (
            session_id TEXT PRIMARY KEY,
            market_ids TEXT,
            wallet_addresses TEXT,
            status TEXT DEFAULT 'active',
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_time TIMESTAMP,
            trades_monitored INTEGER DEFAULT 0,
            whales_detected INTEGER DEFAULT 0
        )
        """)

        self.conn.commit()

    def insert_trade(self, trade: dict, source: str = "subgraph") -> bool:
        """Insert a trade record.

        Args:
            trade: Trade data dictionary
            source: Source of trade data (subgraph, api, etc.)

        Returns:
            True if inserted, False if already exists
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
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
                trade.get("shares"),
                trade.get("price"),
                trade.get("fee"),
                trade.get("transaction_hash") or trade.get("transactionHash"),
                source
            ))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def insert_trades_batch(self, trades: list[dict], source: str = "subgraph") -> int:
        """Insert multiple trades.

        Args:
            trades: List of trade dictionaries
            source: Source of trade data

        Returns:
            Number of trades inserted
        """
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
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT * FROM trades
        WHERE maker = ? OR taker = ?
        ORDER BY timestamp DESC
        """, (wallet, wallet))
        return [dict(row) for row in cursor.fetchall()]

    def get_trades_by_market(self, condition_id: str) -> list[dict]:
        """Retrieve all trades for a market.

        Args:
            condition_id: Market condition ID

        Returns:
            List of trade records
        """
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT * FROM trades
        WHERE condition_id = ?
        ORDER BY timestamp DESC
        """, (condition_id,))
        return [dict(row) for row in cursor.fetchall()]

    def get_whale_wallets(self, min_trades: int = 3, min_volume: float = 5000) -> list[dict]:
        """Retrieve wallets matching whale criteria.

        Args:
            min_trades: Minimum number of trades
            min_volume: Minimum total trade volume

        Returns:
            List of whale wallet records
        """
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT * FROM whale_wallets
        WHERE total_trades >= ? AND total_volume >= ?
        ORDER BY total_volume DESC
        """, (min_trades, min_volume))
        return [dict(row) for row in cursor.fetchall()]

    def update_whale_stats(self, wallet: str):
        """Calculate and update whale statistics for a wallet.

        Args:
            wallet: Wallet address
        """
        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT
            COUNT(*) as total_trades,
            SUM(shares * price) as total_volume,
            AVG(shares * price) as avg_trade_size,
            MIN(timestamp) as first_trade,
            MAX(timestamp) as last_trade,
            COUNT(DISTINCT condition_id) as markets_traded
        FROM trades
        WHERE maker = ? OR taker = ?
        """, (wallet, wallet))

        row = cursor.fetchone()
        if row:
            cursor.execute("""
            INSERT OR REPLACE INTO whale_wallets
            (wallet, total_trades, total_volume, avg_trade_size,
             first_trade_timestamp, last_trade_timestamp, markets_traded)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                wallet,
                row[0],
                row[1],
                row[2],
                row[3],
                row[4],
                row[5]
            ))
            self.conn.commit()

    def update_market_analytics(self, condition_id: str):
        """Calculate and update analytics for a market.

        Args:
            condition_id: Market condition ID
        """
        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT
            COUNT(*) as total_trades,
            SUM(shares * price) as total_volume,
            MIN(timestamp) as first_trade,
            MAX(timestamp) as last_trade
        FROM trades
        WHERE condition_id = ?
        """, (condition_id,))

        row = cursor.fetchone()
        if row:
            # Count whale trades (large volume)
            cursor.execute("""
            SELECT COUNT(*) FROM trades
            WHERE condition_id = ? AND (shares * price) >= 5000
            """, (condition_id,))

            whale_count = cursor.fetchone()[0]

            # Count unique wallets
            cursor.execute("""
            SELECT COUNT(DISTINCT wallet) FROM (
                SELECT DISTINCT maker as wallet FROM trades WHERE condition_id = ?
                UNION
                SELECT DISTINCT taker as wallet FROM trades WHERE condition_id = ?
            )
            """, (condition_id, condition_id))

            unique_wallets = cursor.fetchone()[0]

            cursor.execute("""
            INSERT OR REPLACE INTO market_analytics
            (condition_id, total_trades, total_volume, unique_wallets,
             whale_trades, first_trade_timestamp, last_trade_timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                condition_id,
                row[0],
                row[1],
                unique_wallets,
                whale_count,
                row[2],
                row[3]
            ))
            self.conn.commit()

    def get_market_analytics(self, condition_id: str) -> dict:
        """Get analytics for a market.

        Args:
            condition_id: Market condition ID

        Returns:
            Market analytics record
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM market_analytics WHERE condition_id = ?", (condition_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_recent_trades(self, limit: int = 100) -> list[dict]:
        """Get most recent trades across all markets.

        Args:
            limit: Number of trades to return

        Returns:
            List of recent trade records
        """
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT * FROM trades
        ORDER BY timestamp DESC
        LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]

    def export_to_json(self, filename: str):
        """Export all trades to JSON file.

        Args:
            filename: Output JSON file path
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM trades ORDER BY timestamp DESC")
        trades = [dict(row) for row in cursor.fetchall()]

        with open(filename, "w") as f:
            json.dump(trades, f, indent=2, default=str)

    def close(self):
        """Close database connection."""
        self.conn.close()
