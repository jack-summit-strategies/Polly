from .APIs.gamma import GammaAPI
from .APIs.data import DataAPI
from .APIs.clob import ClobAPI
from .APIs.subgraph import Subgraph


class Polymarket:
    def __init__(self, timeout: int = 10, subgraph_api_key: str = None, subgraph_jwt_token: str = None):
        self.gamma = GammaAPI(timeout=timeout)
        self.data = DataAPI(timeout=timeout)
        self.clob = ClobAPI(timeout=timeout)
        self.subgraph = Subgraph(api_key=subgraph_api_key, jwt_token=subgraph_jwt_token)
