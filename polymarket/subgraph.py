from __future__ import annotations
import requests
from typing import Any


class PolymarketSubgraph:
    """Client for querying Polymarket data from The Graph subgraph."""

    BASE_URL = "https://gateway.thegraph.com/api/[api-key]/subgraphs/id/81Dm16JjuFSrqz813HysXoUPvzTwE7fsfPk2RTf66nyC"
    # Note: Replace [api-key] with your actual API key from https://thegraph.com/studio

    def __init__(self, api_key: str = None):
        """Initialize subgraph client.

        Args:
            api_key: The Graph API key. If None, uses public endpoint (rate limited).
        """
        self.api_key = api_key
        if api_key:
            self.endpoint = f"https://gateway.thegraph.com/api/{api_key}/subgraphs/id/81Dm16JjuFSrqz813HysXoUPvzTwE7fsfPk2RTf66nyC"
        else:
            # Public endpoint without auth
            self.endpoint = "https://arbitrum.thegraph.com/subgraphs/name/polymarket/polymarket"

    def _query(self, query_string: str) -> dict:
        """Execute a GraphQL query.

        Args:
            query_string: GraphQL query string

        Returns:
            Response data dictionary
        """
        payload = {"query": query_string}
        response = requests.post(self.endpoint, json=payload, timeout=30)
        response.raise_for_status()

        data = response.json()

        if "errors" in data:
            raise Exception(f"GraphQL error: {data['errors']}")

        return data.get("data", {})

    def get_market_trades(self, condition_id: str, first: int = 1000, skip: int = 0) -> list[dict]:
        """Fetch trades for a specific market condition.

        Args:
            condition_id: The market condition ID (0x-prefixed hex)
            first: Number of trades to fetch (max 1000)
            skip: Number of trades to skip (for pagination)

        Returns:
            List of trade records
        """
        query = f"""
        query {{
            orderFilleds(
                first: {first}
                skip: {skip}
                where: {{condition: "{condition_id}"}}
                orderBy: timestamp
                orderDirection: desc
            ) {{
                id
                transactionHash
                timestamp
                maker
                taker
                assetId
                outcome
                shares
                price
                fee
            }}
        }}
        """

        result = self._query(query)
        return result.get("orderFilleds", [])

    def get_wallet_trades(self, wallet: str, first: int = 1000, skip: int = 0) -> list[dict]:
        """Fetch all trades by a specific wallet.

        Args:
            wallet: Wallet address (0x-prefixed)
            first: Number of trades to fetch
            skip: Number of trades to skip

        Returns:
            List of trade records
        """
        query = f"""
        query {{
            orderFilleds(
                first: {first}
                skip: {skip}
                where: {{or: [{{maker: "{wallet}"}}, {{taker: "{wallet}"}}]}}
                orderBy: timestamp
                orderDirection: desc
            ) {{
                id
                timestamp
                maker
                taker
                assetId
                outcome
                shares
                price
                condition
            }}
        }}
        """

        result = self._query(query)
        return result.get("orderFilleds", [])

    def get_large_trades(self, min_shares: int = 10000, first: int = 1000, skip: int = 0) -> list[dict]:
        """Fetch large trades (whale activity).

        Args:
            min_shares: Minimum trade size in shares
            first: Number of trades to fetch
            skip: Number of trades to skip

        Returns:
            List of large trade records
        """
        query = f"""
        query {{
            orderFilleds(
                first: {first}
                skip: {skip}
                where: {{shares_gte: {min_shares}}}
                orderBy: timestamp
                orderDirection: desc
            ) {{
                id
                timestamp
                maker
                taker
                shares
                price
                condition
                outcome
                assetId
                transactionHash
            }}
        }}
        """

        result = self._query(query)
        return result.get("orderFilleds", [])

    def get_trades_by_time_range(self, start_time: int, end_time: int, first: int = 1000) -> list[dict]:
        """Fetch trades within a time range.

        Args:
            start_time: Unix timestamp (seconds) for start
            end_time: Unix timestamp (seconds) for end
            first: Number of trades to fetch

        Returns:
            List of trade records
        """
        query = f"""
        query {{
            orderFilleds(
                first: {first}
                where: {{timestamp_gte: {start_time}, timestamp_lte: {end_time}}}
                orderBy: timestamp
                orderDirection: desc
            ) {{
                id
                timestamp
                maker
                taker
                shares
                price
                condition
                outcome
            }}
        }}
        """

        result = self._query(query)
        return result.get("orderFilleds", [])

    def get_market_positions(self, condition_id: str, first: int = 1000) -> list[dict]:
        """Fetch current positions in a market.

        Args:
            condition_id: Market condition ID
            first: Number of positions to fetch

        Returns:
            List of position records
        """
        query = f"""
        query {{
            positions(
                first: {first}
                where: {{condition: "{condition_id}"}}
            ) {{
                id
                user
                balance
                outcome
                condition
            }}
        }}
        """

        result = self._query(query)
        return result.get("positions", [])

    def get_market_info(self, condition_id: str) -> dict:
        """Fetch metadata for a market.

        Args:
            condition_id: Market condition ID

        Returns:
            Market metadata
        """
        query = f"""
        query {{
            conditions(where: {{id: "{condition_id}"}}) {{
                id
                eventId
                questionId
                resolution
                resolutionTimestamp
            }}
        }}
        """

        result = self._query(query)
        conditions = result.get("conditions", [])
        return conditions[0] if conditions else None
