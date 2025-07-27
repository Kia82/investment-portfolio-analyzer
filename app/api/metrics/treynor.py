
from app.api.metrics.base_metric import BaseMetric
import pandas as pd
class TreynorRatio(BaseMetric):

    def __init__(self, cache_ttl: int = 3600):
        super().__init__(cache_ttl=cache_ttl)

    def _calculate_stats(self, positions_data: pd.DataFrame):
        """
        
        """

        