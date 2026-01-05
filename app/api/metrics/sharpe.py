from cmath import sqrt
from .base_metric import BaseMetric
import numpy as np
import logging
import pandas as pd
from api.simple_stat_calculations import SimpleStatCalculations
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SharpeRatio(BaseMetric, SimpleStatCalculations):
   
    def __init__(self, cache_ttl: int = 3600):
        super().__init__(cache_ttl=cache_ttl)

    @staticmethod
    def _calculate_stats(positions_data: pd.DataFrame):
        """
        Given the stock data of each ticker, calculates the standard deviation and mean of each symbol's close 

        Note:
          positions_data accepts only a specific type of data frame (get_stock_bars from alpaca-py sdk).
        """
        simple_stat_calculations = SimpleStatCalculations(positions_data)
        mean = simple_stat_calculations.calculate_mean()
        std = simple_stat_calculations.calculate_std()
        return {"overall_return" : mean, "volatility" : std}
    
    def compute(self, positions_data, symbols, daily_risk_rate: float = 0.000119):
        return super().compute(positions_data,symbols,daily_risk_rate)
        