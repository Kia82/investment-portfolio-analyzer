from api.base import Base
class BaseMetric(Base):
    def __init__(self, cache_ttl: int):
        super().__init__(cache_ttl=cache_ttl)

    def compute(self):
        raise NotImplementedError("Each metric must implement compute().")
