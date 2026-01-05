from cmath import sqrt
from .base_metric import BaseMetric
import logging
import pandas as pd
from api.simple_stat_calculations import SimpleStatCalculations

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

class SortinoRatio(BaseMetric, SimpleStatCalculations):
   
    def __init__(self, cache_ttl: int = 3600):
        super().__init__(cache_ttl=cache_ttl)

    @staticmethod
    def _calculate_stats(positions_data: pd.DataFrame):
        """
        Given the stock data of each ticker, calculates the standard deviation and mean with data of each day's close given the return that day is less 
        than 0 (negative)  

        Note:
          positions_data accepts only a specific type of data frame (get_stock_bars from alpaca-py sdk).
        """
        daily_returns = positions_data.groupby("symbol")["close"].pct_change().dropna()

        mean = daily_returns.groupby("symbol").mean().to_dict()
        negative_returns = daily_returns[daily_returns < 0]
        std = negative_returns.groupby("symbol").std().to_dict()
        return {"overall_return" : mean, "volatility" : std}

    def compute(self, positions_data, symbols, daily_risk_rate: float = 0.000119):
        return super().compute(positions_data,symbols,daily_risk_rate)
        