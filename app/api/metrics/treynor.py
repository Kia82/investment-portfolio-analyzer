
from api.metrics.base_metric import BaseMetric
import pandas as pd
class TreynorRatio(BaseMetric):

    def __init__(self, cache_ttl: int = 3600):
        super().__init__(cache_ttl=cache_ttl)

    def _calculate_stats(self, positions_data: pd.DataFrame):
        """
         Given the stock data of each ticket, we calculate the porfolio's return
        """
        daily_returns = positions_data.groupby("symbol")["close"].pct_change().dropna()
        overall_return = daily_returns.groupby("symbol").mean().to_dict()
        # The volatility is equal to the overall return for the sake of a demo purposes. Future development should make this
        # properly functional 
        volatility = overall_return
        return {"overall_return": overall_return, "volatility": volatility}

    def compute(self, positions_data, symbols, daily_risk_rate:float = 0.000119):
        return super().compute(positions_data,symbols,daily_risk_rate)
    


        