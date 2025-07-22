from cmath import sqrt
from typing import Optional
from alpaca_api import AlpacaStockHistoricalDataClient
from portfolio import PortfolioManager
from portfolio import PortfolioManager
from dotenv import load_dotenv
from alpaca.data.timeframe import TimeFrame
from datetime import date, timedelta
from datetime import date, timedelta
from alpaca.common.enums import SupportedCurrencies
from functools import lru_cache
import requests
import os
import logging
import numpy as np
import pandas


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
        cache_ttl: int = 3600 # Cache TTL in seconds
    ):
        self.clientStockAnalysis = AlpacaStockHistoricalDataClient(
            api_key=api_key, api_secret=api_secret)
        self.start_date = start
        self.end_date = end
        self.timeframe = timeframe
        self.currency = currency
        self.cache_ttl = cache_ttl

        # Cache for expensive operations
        self._risk_free_rate_cache = None
        self._risk_free_rate_timestamp = None
        self._historical_data_cache = {}
        self._historical_data_timestamp = None
        self.portfolio_manager = PortfolioManager(api_key=api_key, api_secret=api_secret)

    # grabs the most recent US treasury's risk free rate using the 10 year
    def _get_risk_free_rate(self) -> float:
        current_time = pandas.Timestamp.now()
        
        if (self._risk_free_rate_cache is not None and
            self._risk_free_rate_timestamp is not None and
            (current_time - self._risk_free_rate_timestamp).total_seconds() < self.cache_ttl):
            return self._risk_free_rate_cache
        
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
                return 0.04  # Default 4% if API fails
            
            self._risk_free_rate_cache=ten_year_treasury_rate= data[0]["year10"]
            self._risk_free_rate_timestamp=current_time
            return ten_year_treasury_rate
        except Exception as e:
            logger.error(f'Error fetching risk-free rate: {e}')
            return 0.04
    
    def _get_historical_data(self, symbol_or_symbols):
        cache_key = f"{'-'.join(sorted(symbol_or_symbols))}_{self.start_date}_{self.end_date}"

        if cache_key in self._historical_data_cache:
            return self._historical_data_cache[cache_key]
        
        try: 
            response_df = self.clientStockAnalysis.get_historical_data(
                symbol_or_symbols=symbol_or_symbols,
                start=self.start_date,
                end=self.end_date,
                timeframe=self.timeframe,
                currency=self.currency,
            )
            self._historical_data_cache[cache_key] = response_df
            return response_df
        
        except Exception as e:
            logger.error(f"Error fetching historical data of symbol(s): {e}")
            raise
    
    def _calculate_returns_and_stats_vectorized(self, symbol_or_symbols):
        stock_data = self._get_historical_data(symbol_or_symbols=symbol_or_symbols)
        daily_returns = stock_data.groupby("symbol")["close"].pct_change().dropna()
        mean = daily_returns.groupby("symbol").mean().to_dict()
        standard_deviation = daily_returns.groupby("symbol").std().to_dict()
        return {"mean" : mean, "std" : standard_deviation}

    def sharpe_ratio(self, risk_rate: Optional[float] = None):
        """Calculates the annual sharpe ratio using daily statistics"""
        positions_sharpe = {}
        portfolio_sharpe = 0

        # weight of positions in portfolio used for grabbing portfolio positions and
        # portfolio sharpe calculation 
        position_weights = self.portfolio_manager.weights_of_positions()
        symbols = list(position_weights.keys())
        if not symbols:
            logger.warning("No positions found in portfolio")
            return {"positions_sharpe": positions_sharpe, "portfolio_sharpe": portfolio_sharpe}
        returns_stats = self._calculate_returns_and_stats_vectorized(
            symbol_or_symbols=symbols)
        
        if risk_rate is None:
            risk_rate = self._get_risk_free_rate()
        
        risk_rate_to_decimal = risk_rate/100
        daily_risk_rate = risk_rate_to_decimal/252
        sqrt_252 = sqrt(252).real
      
        for symbol in symbols:
            mean_return = returns_stats["mean"].get(symbol, 0)
            std_return = returns_stats["std"].get(symbol,1)

            if std_return > 0:
                sharpe = (mean_return - daily_risk_rate)/std_return * sqrt_252
                positions_sharpe[symbol] = sharpe
                portfolio_sharpe += sharpe * position_weights[symbol]

            else:
                positions_sharpe[symbol] = 0.0
        return {"positions_sharpe": positions_sharpe, "portfolio_sharpe": portfolio_sharpe} 
    
    def batch_calculate_metrics(self, symbols):
        """Calculate multiple metrics in a single batch operation"""
        returns_stats = self._calculate_returns_and_stats_vectorized(symbols)
        risk_rate = self._get_risk_free_rate()
        
        results = {}
        daily_risk_rate = risk_rate / (100 * 252)
        sqrt_252 = sqrt(252).real
        
        for symbol in symbols:
            mean_return = returns_stats["mean"].get(symbol, 0)
            std_return = returns_stats["std"].get(symbol, 1)
            
            sharpe = ((mean_return - daily_risk_rate) / std_return) * sqrt_252 if std_return > 0 else 0
            
            results[symbol] = {
                "mean_return": mean_return,
                "std_return": std_return,
                "sharpe_ratio": sharpe,
                "annualized_return": mean_return * 252,
                "annualized_volatility": std_return * sqrt_252
            }
            
        return results
    
    def sortino_ratio(self, benchmark: Optional[float] = None):
        if benchmark is None:
            risk_rate = self._get_risk_free_rate()
    
    def clear_cache(self):  
        """Clear all cached data"""
        self._risk_free_rate_cache = None
        self._risk_free_rate_timestamp = None
        self._historical_data_cache.clear()
        self._portfolio_weights_cache = None
        self._portfolio_weights_timestamp = None

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
    sharpe = client.sharpe_ratio()
    print(f"Sharpe of Individual Positions: {sharpe['positions_sharpe']}")
    print(f"Portfolio Sharpe: {sharpe['portfolio_sharpe']}")
    
    print(client.batch_calculate_metrics(["AAPL", "NVIDIA", "SPY"]))
    print(client.batch_calculate_metrics(["AAPL", "NVIDIA", "SPY"]))