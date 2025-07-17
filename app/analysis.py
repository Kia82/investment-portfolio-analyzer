from cmath import sqrt
from typing import Optional

from pandas import DataFrame
from alpaca_api import AlpacaStockHistoricalDataClient
from portfolio import PortfolioManager
from dotenv import load_dotenv
from alpaca.data.timeframe import TimeFrame
from datetime import date, timedelta
from alpaca.common.enums import SupportedCurrencies
import requests
import os
import numpy as np

class AnalysisManager:

    # To analyze stock, user needs to initialize their symbols, start/end at minimum
    def __init__(
        self,
        api_key,
        api_secret,
        start,
        end,
        timeframe=TimeFrame.Day,
        currency=SupportedCurrencies.USD,
    ):
        self.clientStockAnalysis = AlpacaStockHistoricalDataClient(
            api_key=api_key, api_secret=api_secret
        )
        self.start_date = start
        self.end_date = end
        self.timeframe = timeframe
        self.currency = currency
        self.daily_return: float

    @staticmethod
    # grabs the most recent US treasury's risk free rate using the 10 year
    def __fetch_risk_free_rate() -> float:
        # filtering output based on last week to reduce response size and
        # ensure we are always getting a response
        today = date.today()
        last_week = today - timedelta(days=10)
        fmp_key = os.getenv("FMP_KEY")
        url = "https://financialmodelingprep.com/stable/treasury-rates"
        response = requests.request(
            "GET",
            url=url,
            params={"from": last_week.strftime("%Y-%m-%d"), "apikey": fmp_key},
        )

        data = response.json()
        most_recent_trading_date = data[0]
        ten_year_treasury_rate = most_recent_trading_date["year10"]
        return ten_year_treasury_rate
    
    def __get_historical_data(self, symbol_or_symbols):
        response_df = self.clientStockAnalysis.get_historical_data(
            symbol_or_symbols=symbol_or_symbols,
            start=self.start_date,
            end=self.end_date,
            timeframe=self.timeframe,
            currency=self.currency,
        )
        return response_df
    
    def __daily_stock_return_and_std(self, symbol_or_symbols):
        stock_data = self.__get_historical_data(symbol_or_symbols=symbol_or_symbols)
        daily_ret = stock_data.groupby("symbol")["close"].pct_change()

        mean = daily_ret.groupby("symbol").mean().to_dict()
        standard_deviation = daily_ret.groupby("symbol").std().to_dict()
        return {"mean" : mean, "std" : standard_deviation}

    def calculate_sharpe_ratio(self, risk_rate: Optional[float] = None):
        # weight of positions in portfolio used for grabbing portfolio positions and
        # portfolio sharpe calculation 
        client_portfolio = PortfolioManager(api_key=api_key, api_secret=api_secret)
        position_weights = client_portfolio.weights_of_positions()
        symbol_or_symbols = []
        for pos in position_weights:
            symbol_or_symbols.append(pos)
        average_daily_returns = self.__daily_stock_return_and_std(
            symbol_or_symbols=symbol_or_symbols
        )
        if risk_rate  is None:
            risk_rate = self.__fetch_risk_free_rate()
        position_returns = average_daily_returns
        daily_risk_rate = risk_rate/(100*252)
        annual_position_sharpe = {}
        annual_portfolio_sharpe = 0
        for k in position_returns["mean"]:
            annual_position_sharpe[k] = ((position_returns['mean'][k] - daily_risk_rate)/(position_returns['std'][k]) * sqrt(252)).real
            annual_portfolio_sharpe += annual_position_sharpe[k]*position_weights[k]
        return {"positions_sharpe": annual_position_sharpe, "portfolio_sharpe": annual_portfolio_sharpe} 
    
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
    sharpe = client.calculate_sharpe_ratio()
    print(sharpe['positions_sharpe'])
    print(sharpe['portfolio_sharpe'])