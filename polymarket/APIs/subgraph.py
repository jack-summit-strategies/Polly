from __future__ import annotations
import requests
from typing import Any
from ..contracts.subgraph import MarketActivityParams, MarketActivityResponse


class Subgraph:
    """Client for querying Polymarket data from The Graph subgraph."""

    BASE_URL = "https://gateway.thegraph.com/api/[api-key]/subgraphs/id/81Dm16JjuFSrqz813HysXoUPvzTwE7fsfPk2RTf66nyC"
    TOKENS_URL = "https://token-api.thegraph.com/v1/polymarket/markets/activity"


    def __init__(self, api_key: str = None, jwt_token: str = None):
        self.api_key = api_key
        self.jwt_token = jwt_token

        if api_key:
            self.endpoint = f"https://gateway.thegraph.com/api/{api_key}/subgraphs/id/81Dm16JjuFSrqz813HysXoUPvzTwE7fsfPk2RTf66nyC"
        else:
            self.endpoint = "https://arbitrum.thegraph.com/subgraphs/name/polymarket/polymarket"


    #
    #   GraphQL Functions
    #

    #Execute GraphQL query and return response data.
    def _query(self, query_string: str) -> dict:
        payload = {"query": query_string}
        response = requests.post(self.endpoint, json=payload, headers={"Authorization": f"Bearer {self.jwt_token}"}, timeout=30)
        response.raise_for_status()

        data = response.json()

        if "errors" in data:
            raise Exception(f"GraphQL error: {data['errors']}")

        return data.get("data", {})

    #Fetch trades for a market (paginated)
    def get_market_trades(self, condition_id: str, first: int = 1000, skip: int = 0) -> list[dict]:

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

    #Fetch trades by wallet (paginated)
    def get_wallet_trades(self, wallet: str, first: int = 1000, skip: int = 0) -> list[dict]:

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

    #Fetch large trades by minimum share size
    def get_large_trades(self, min_shares: int = 10000, first: int = 1000, skip: int = 0) -> list[dict]:

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

    #Fetch trades within Unix timestamp range.
    def get_trades_by_time_range(self, start_time: int, end_time: int, first: int = 1000) -> list[dict]:

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

    #Fetch current positions for a market.
    def get_market_positions(self, condition_id: str, first: int = 1000) -> list[dict]:

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

    #Fetch market metadata
    def get_market_info(self, condition_id: str) -> dict:

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


    #
    #   Rest Functions
    #

    # Fetch first page of market activity only
    def get_market_activity_page(self, params: MarketActivityParams) -> MarketActivityResponse:
        query = {k: v for k, v in params.model_dump().items() if v is not None}
        query["page"] = 1
        response = requests.get(
            self.TOKENS_URL,
            params=query,
            headers={"Authorization": f"Bearer {self.jwt_token}"},
            timeout=30,
        )
        response.raise_for_status()
        return MarketActivityResponse.model_validate(response.json())

    #Fetch all market activity from the Market API, paginating until data is empty
    def get_market_activity(self, params: MarketActivityParams) -> MarketActivityResponse:
        base_query = {k: v for k, v in params.model_dump().items() if v is not None}
        base_query["limit"] = 10
        all_data = []
        page = 1

        while True:
            base_query["page"] = page
            response = requests.get(
                self.TOKENS_URL,
                params=base_query,
                headers={"Authorization": f"Bearer {self.jwt_token}"},
                timeout=30,
            )
            response.raise_for_status()
            result = MarketActivityResponse.model_validate(response.json())
            if not result.data:
                break
            all_data.extend(result.data)
            page += 1

        return MarketActivityResponse(data=all_data)
