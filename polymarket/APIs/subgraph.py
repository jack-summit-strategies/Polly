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
