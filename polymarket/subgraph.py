from __future__ import annotations
import requests
from typing import Any


class PolymarketSubgraph:
    """Client for querying Polymarket data from The Graph subgraph."""

    BASE_URL = "https://gateway.thegraph.com/api/[api-key]/subgraphs/id/81Dm16JjuFSrqz813HysXoUPvzTwE7fsfPk2RTf66nyC"

    def __init__(self, api_key: str = None):
        """Init client with optional API key. Uses public endpoint if None."""
        self.api_key = api_key
        if api_key:
            self.endpoint = f"https://gateway.thegraph.com/api/{api_key}/subgraphs/id/81Dm16JjuFSrqz813HysXoUPvzTwE7fsfPk2RTf66nyC"
        else:
            self.endpoint = "https://arbitrum.thegraph.com/subgraphs/name/polymarket/polymarket"

    def _query(self, query_string: str) -> dict:
        """Execute GraphQL query and return response data."""
        payload = {"query": query_string}
        response = requests.post(self.endpoint, json=payload, timeout=30)
        response.raise_for_status()

        data = response.json()

        if "errors" in data:
            raise Exception(f"GraphQL error: {data['errors']}")

        return data.get("data", {})

    def get_market_trades(self, condition_id: str, first: int = 1000, skip: int = 0) -> list[dict]:
        """Fetch trades for a market (paginated)."""
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
        """Fetch trades by wallet (paginated)."""
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
        """Fetch large trades by minimum share size."""
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
        """Fetch trades within Unix timestamp range."""
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
        """Fetch current positions for a market."""
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
        """Fetch market metadata."""
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
