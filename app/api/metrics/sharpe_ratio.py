from cmath import sqrt
from .base_metric import BaseMetric
import numpy as np
import logging
import pandas as pd
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SharpeRatio(BaseMetric):
    """a couple things to note, positions_data accepts only a specific type of data frame (get_stock_bars from alpaca-py sdk).
        You can see how we use it in the private function _calculate_returns_and_stats_vectorized """

    def __init__(self, cache_ttl: int = 3600):
        super().__init__(cache_ttl=cache_ttl)

    def _calculate_stats_dict(self, positions_data: pd.DataFrame):
        daily_returns = positions_data.groupby("symbol")["close"].pct_change().dropna()
        mean = daily_returns.groupby("symbol").mean().to_dict()
        standard_deviation = daily_returns.groupby("symbol").std().to_dict()
        return {"mean" : mean, "std" : standard_deviation}

    def compute(self, positions_data, symbols, daily_risk_rate: float = 0.000119):
        cache_key = self._cache_key(*symbols, risk_rate=daily_risk_rate)
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        results = {}
        return_stats = self._calculate_stats_dict(positions_data=positions_data)
        for symbol in symbols:
            mean_return = return_stats['mean'].get(symbol, 0)
            std_return = return_stats['std'].get(symbol,1)

            if std_return > 0:
                sqrt_252 = sqrt(252).real
                sharpe = ((mean_return-daily_risk_rate)/std_return) * sqrt_252
            else:
                logger.error(ValueError("Standard deviation of returns is zero; Sharpe Ratio is undefined."))
                raise
            results[symbol] = sharpe
        self.cache.set(cache_key, results)
        return results
        