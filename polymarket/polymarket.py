from .APIs.gamma import GammaAPI
from .APIs.data import DataAPI
from .APIs.clob import ClobAPI


class Polymarket:
    def __init__(self, timeout: int = 10):
        self.gamma = GammaAPI(timeout=timeout)
        self.data = DataAPI(timeout=timeout)
        self.clob = ClobAPI(timeout=timeout)
