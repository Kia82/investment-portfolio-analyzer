import logging
import os
from datetime import date, timedelta
from math import sqrt
from typing import Optional
from dotenv import load_dotenv
from alpaca.common.enums import SupportedCurrencies
from alpaca.data.timeframe import TimeFrame
from api.alpaca_api import AlpacaStockHistoricalDataClient
from api.metrics.risk_free_rate import RiskFreeRate
from api.metrics.sharpe import SharpeRatio
from api.metrics.sortino import SortinoRatio
# from api.metrics.treynor import TreynorRatio
from portfolio import PortfolioManager

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
        self._risk_free_rate = RiskFreeRate(cache_ttl=cache_ttl*48) # equivalent to  2 days 
        
        # Metrics
        self._sharpe_ratio = SharpeRatio(cache_ttl=cache_ttl)
        self._sortino_ratio = SortinoRatio(cache_ttl=cache_ttl)

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
    
    # def batch_calculate_metrics(self, symbols):
    #     """Calculate multiple metrics in a single batch operation"""
    #     return_stats = self._calculate_returns_and_stats_vectorized(symbols)
    #     risk_rate = self._get_daily_risk_free_rate()
        
    #     results = {}
    #     daily_risk_rate = risk_rate
    #     sqrt_252 = sqrt(252).real
        
    #     for symbol in symbols:
    #         mean_return = return_stats["mean"].get(symbol, 0)
    #         std_return = return_stats["std"].get(symbol, 1)
            
    #         if std_return > 0:
    #             sharpe = ((mean_return - daily_risk_rate) / std_return) * sqrt_252
    #         else:
    #             logger.error(ValueError("Standard deviation of returns is zero; Sharpe Ratio is undefined."))
    #             raise
            
    #         results[symbol] = {
    #             "mean_return": mean_return,
    #             "std_return": std_return,
    #             "sharpe_ratio": sharpe,
    #             "annualized_return": mean_return * 252,
    #             "annualized_volatility": std_return * sqrt_252
    #         }
            
    #     return results
    
    def calculate_sortino_ratio(self, risk_rate: Optional[float] = None):
        """Calculates the sortino ratio with the chosen risk free rate
        
        Args:
            risk_rate: the yearly risk free rate/benchmark rate
        """
        positions_sortino = {}
        portfolio_sortino = 0

        # weight of positions in portfolio used for grabbing portfolio positions and
        # portfolio sharpe calculation 
        position_weights = self.portfolio_manager.weights_of_positions()
        daily_risk_rate = risk_rate/252 if risk_rate else self.calculate_risk_free_rate()

        symbols = list(position_weights.keys())
        if not symbols:
            logger.warning("No positions found in portfolio")
            return {"positions_sharpe": positions_sortino, "portfolio_sharpe": portfolio_sortino}

        positions_data = self._get_historical_data(symbols)
        positions_sortino = self._sortino_ratio.compute(positions_data=positions_data,symbols=symbols, daily_risk_rate=daily_risk_rate)

        for k in position_weights:
            portfolio_sortino += position_weights[k] * positions_sortino[k]
        return {"positions_sortino": positions_sortino, "portfolio_sortino": portfolio_sortino} 
    
if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("APCA_KEY")
    api_secret = os.getenv("APCA_SECRET")
    today = date.today()
    ten_years_ago = today - timedelta(weeks=520)
    today_formatted = today.strftime("%Y-%m-%d")
    ten_years_ago_formatted = ten_years_ago.strftime("%Y-%m-%d")

    client = AnalysisManager(
        api_key=api_key,
        api_secret=api_secret,
        start=ten_years_ago_formatted,
        end=today_formatted,
    )

    for i in range(100):
        print(client.calculate_sortino_ratio())
        print(client.calculate_sharpe_ratio())
