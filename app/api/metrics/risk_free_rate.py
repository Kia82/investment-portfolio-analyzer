from .base_metric import BaseMetric
from enum import Enum
from datetime import timedelta, date
import logging
import sigfig
import os
import requests
# from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RateFrequency(Enum):
    DAILY = 252
    MONTHLY = 12
    YEARLY = 1

class RiskFreeRate(BaseMetric):

    def __init__(self, cache_ttl: int = 3600):
        super().__init__(cache_ttl=cache_ttl)

    def compute(self, frequency: RateFrequency = RateFrequency.DAILY) -> float:
        """
        Get risk-free rate for specified frequency
        
        Args:
            frequency: RateFrequency enum specifying return frequency
            
        Returns:
            float: Risk-free rate for specified frequency
        """
        cache_key = self._cache_key("risk_rate")
        cached_result = self.cache.get(cache_key)

        if cached_result is not None:
            return cached_result
        
        default_risk_rate = 0.04 / frequency.value  # 4% annual rate converted to specified frequency

        try:
            today = date.today()
            last_week = today - timedelta(days=5)
            
            fmp_key = os.getenv("FMP_KEY")
            url = "https://financialmodelingprep.com/stable/treasury-rates"
            response = requests.request(
                "GET",
                url=url,
                params={"from": last_week.strftime("%Y-%m-%d"), "apikey": fmp_key},
                timeout=10
            )
            response.raise_for_status()

            # filtering output based on last week to reduce response size and
            # ensure we can get some response (longest Consecutive Non-Trading day is 3 days)
            data = response.json()

            if not data:
                logger.warning("No treasury data received, using default rate")
                return default_risk_rate  
            
            rate = sigfig.round(data[0]["year10"] / (100 * frequency.value), sigfigs=3)
            self.cache.set(cache_key, rate)
            return rate
            
        except Exception as e:
            logger.error(f' Fetching risk-free rate: {e}')
            return default_risk_rate