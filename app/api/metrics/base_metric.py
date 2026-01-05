import logging
from api.base import Base
from cmath import sqrt

class BaseMetric(Base):
    def __init__(self, cache_ttl: int):
        super().__init__(cache_ttl=cache_ttl)

    def compute(self, positions_data, symbols, daily_risk_rate: float = 0.000119):
        cache_key = self._cache_key(*symbols, risk_rate=daily_risk_rate)
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        results = {}
        return_stats = self._calculate_stats(positions_data)
        for symbol in symbols:
            overall_return = return_stats['overall_return'].get(symbol, 0)
            volatility = return_stats['volatility'].get(symbol,1)

            if volatility > 0:
                sqrt_252 = sqrt(252).real
                ratio = ((overall_return-daily_risk_rate)/volatility) * sqrt_252
            else:
                self.logger.error("Standard deviation of returns is zero; ratio is undefined.")
                raise ValueError("Standard deviation of returns is zero; ratio is undefined.")
            results[symbol] = ratio
        self.cache.set(cache_key, results)
        return results
