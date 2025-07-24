from cmath import sqrt
from typing import Optional
from app.api.alpaca_api import AlpacaStockHistoricalDataClient
from api.metrics.sharpe_ratio import SharpeRatio
from api.metrics.risk_free_rate import RiskFreeRate
from portfolio import PortfolioManager
from portfolio import PortfolioManager
from dotenv import load_dotenv
from alpaca.data.timeframe import TimeFrame
from datetime import date, timedelta
from datetime import date, timedelta
from alpaca.common.enums import SupportedCurrencies
import os
import logging
import numpy as np


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalysisManager:

    # To analyze stock, user needs to initialize their symbols, start/end at minimum
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        start: str,
        end: str,
        timeframe: TimeFrame =TimeFrame.Day,
        currency: SupportedCurrencies =SupportedCurrencies.USD,
        cache_ttl: int = 3600 # Cache TTL in seconds, 3600 is equivalent to 1 hour
    ):
        self.clientStockAnalysis = AlpacaStockHistoricalDataClient(
            cache_ttl=cache_ttl, 
            api_key=api_key, 
            api_secret=api_secret) 
        self.start_date = start
        self.end_date = end
        self.timeframe = timeframe
        self.currency = currency
        self.cache_ttl = cache_ttl # remove once migration is done

        self.portfolio_manager = PortfolioManager(api_key=api_key, api_secret=api_secret)
        self._sharpe_ratio = SharpeRatio(cache_ttl=cache_ttl)
        self._risk_free_rate = RiskFreeRate(cache_ttl=cache_ttl*48) # equivalent to  2 days 

    # grabs the most recent US treasury's risk free rate using the 10 year
    
    def _get_historical_data(self, symbol_or_symbols):
        try: 
            response_df = self.clientStockAnalysis.get_historical_data(
                symbol_or_symbols=symbol_or_symbols,
                start=self.start_date,
                end=self.end_date,
                timeframe=self.timeframe,
                currency=self.currency,
            )
            return response_df
        
        except Exception as e:
            logger.error(f"Error fetching historical data of symbol(s): {e}")
            raise

    def calculate_risk_free_rate(self):
        return self._risk_free_rate.compute()

    def calculate_sharpe_ratio(self, risk_rate: Optional[float] = None):
        """Calculates the annual sharpe ratio using daily statistics"""
        positions_sharpe = {}
        portfolio_sharpe = 0

        # weight of positions in portfolio used for grabbing portfolio positions and
        # portfolio sharpe calculation 
        position_weights = self.portfolio_manager.weights_of_positions()
        daily_risk_rate = risk_rate/252 if risk_rate else self.calculate_risk_free_rate()

        symbols = list(position_weights.keys())
        if not symbols:
            logger.warning("No positions found in portfolio")
            return {"positions_sharpe": positions_sharpe, "portfolio_sharpe": portfolio_sharpe}
        positions_data = self._get_historical_data(symbols)
    
        positions_sharpe = self._sharpe_ratio.compute(positions_data=positions_data,symbols=symbols, daily_risk_rate=daily_risk_rate)
        
        for k in position_weights:
            portfolio_sharpe += positions_sharpe[k] * position_weights[k] 
        return {"positions_sharpe": positions_sharpe, "portfolio_sharpe": portfolio_sharpe} 
    
    def batch_calculate_metrics(self, symbols):
        """Calculate multiple metrics in a single batch operation"""
        return_stats = self._calculate_returns_and_stats_vectorized(symbols)
        risk_rate = self._get_daily_risk_free_rate()
        
        results = {}
        daily_risk_rate = risk_rate
        sqrt_252 = sqrt(252).real
        
        for symbol in symbols:
            mean_return = return_stats["mean"].get(symbol, 0)
            std_return = return_stats["std"].get(symbol, 1)
            
            if std_return > 0:
                sharpe = ((mean_return - daily_risk_rate) / std_return) * sqrt_252
            else:
                logger.error(ValueError("Standard deviation of returns is zero; Sharpe Ratio is undefined."))
                raise
            
            results[symbol] = {
                "mean_return": mean_return,
                "std_return": std_return,
                "sharpe_ratio": sharpe,
                "annualized_return": mean_return * 252,
                "annualized_volatility": std_return * sqrt_252
            }
            
        return results
    
    def sortino_ratio(self, benchmark: Optional[float] = None):
        pass
        # if benchmark is None:
        # risk_rate = self._get_daily_risk_free_rate()
    
    def clear_cache(self):  
        """Clear all cached data"""
        # self._risk_free_rate_cache = None
        # self._risk_free_rate_timestamp = None
        # self._portfolio_weights_cache = None
        # self._portfolio_weights_timestamp = None

if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("APCA_KEY")
    api_secret = os.getenv("APCA_SECRET")
    today = date.today()
    ten_years_ago = today - timedelta(weeks=520)
    today = today.strftime("%Y-%m-%d")
    ten_years_ago = ten_years_ago.strftime("%Y-%m-%d")

    client = AnalysisManager(
        api_key=api_key,
        api_secret=api_secret,
        start=ten_years_ago,
        end=today,
    )
    for i in range(100):
        sharpe = client.calculate_sharpe_ratio()
        print(sharpe)

