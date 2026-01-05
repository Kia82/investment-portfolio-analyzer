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
from api.metrics.treynor import TreynorRatio
from portfolio_manager import PortfolioManager
from api.simulation.monte_carlo_manager import MonteCarloManager

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
        self._treynor_ratio = TreynorRatio(cache_ttl=cache_ttl)

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
    
    def _daily_risk_rate(self, risk_rate: Optional[float] = None):
        return  risk_rate/252 if risk_rate else self._risk_free_rate.compute()
    

    def _calculate_ratio(self,ratio,tag_name, risk_rate: Optional[float] = None):
        positions_ratio = {}
        portfolio_ratio = 0

        # weight of positions in portfolio used for grabbing portfolio positions and
        # portfolio sharpe calculation 
        position_weights = self.portfolio_manager.weights_of_positions()

        symbols = list(position_weights.keys())
        if not symbols:
            logger.warning("No positions found in portfolio")
            return {"positions_ratio": positions_ratio, "portfolio_ratio": portfolio_ratio}
        positions_data = self._get_historical_data(symbols)
        positions_ratio = ratio.compute(positions_data=positions_data,symbols=symbols, daily_risk_rate=self._daily_risk_rate(risk_rate))

        for k in position_weights:
            portfolio_ratio += positions_ratio[k] * position_weights[k]
        return {"positions_ratio": positions_ratio, "portfolio_ratio": portfolio_ratio}
    


    def calculate_sharpe_ratio(self, risk_rate: Optional[float] = None):
        """Calculates the annual sharpe ratio using daily statistics"""
        return self._calculate_ratio(self._sharpe_ratio,risk_rate)
    
    def calculate_sortino_ratio(self, risk_rate: Optional[float] = None):
        """
        Calculates the sortino ratio with the chosen risk free rate
        
        Args:
            risk_rate: the yearly risk free rate/benchmark rate
        """

        # positions_sortino = {}
        # portfolio_sortino = 0

        # # returns a list containing the weight of each position in the portfolio.
        # # This is used for collecting all the symbols in the portfolio and calculating 
        # position_weights = self.portfolio_manager.weights_of_positions()

        # symbols = list(position_weights.keys())
        # if not symbols:
        #     logger.warning("No positions found in portfolio")
        #     return {"positions_sortino": positions_sortino, "positions_sortino": portfolio_sortino}

        # positions_data = self._get_historical_data(symbols)
        # positions_sortino = self._sortino_ratio.compute(positions_data=positions_data,symbols=symbols, daily_risk_rate=self._daily_risk_rate(risk_rate))

        # for k in position_weights:
        #     portfolio_sortino += position_weights[k] * positions_sortino[k]
        # return {"positions_sortino": positions_sortino, "positions_sortino": portfolio_sortino}
        return self._calculate_ratio(self._sortino_ratio,"sortino)ratio", risk_rate)


    def calculate_treynor_ratio(self, risk_rate: Optional[float] = None):
        """
        calculates a portfolio's treynor ratio. We can optionally input a custom risk rate 
        """
        return self._calculate_ratio(self._treynor_ratio, risk_rate)
        
    def run_monte_carlo_simulation(self,years=5, simulations: int=100):
        """ runs a monte carlo simulation"""

        principal = self.portfolio_manager.account_details().last_equity
        position_weights = self.portfolio_manager.weights_of_positions()
        symbols = list(position_weights.keys())
        historical_positions_data = self._get_historical_data(symbols)

        monte_carlo_sim = MonteCarloManager.prepare_and_run_sim(principal=principal,years=years, 
                                              simulations=simulations, 
                                              position_weights=position_weights,
                                              historical_positions_data=historical_positions_data)
        return monte_carlo_sim
    
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
    result = client.run_monte_carlo_simulation()
    
    mean_portfolio_value = result.meanPortfolioValue
    variance = result.variance
    p_square_quantile = result.pSquareQuantile

    print("Mean Portfolio Value:", int(mean_portfolio_value))
    print("Variance:", int(sqrt(variance)))
    print("P-Square Quantile:", int(p_square_quantile))
    # for i in range(100):
    #     print(client.calculate_sortino_ratio())
    #     print(client.calculate_sharpe_ratio())
