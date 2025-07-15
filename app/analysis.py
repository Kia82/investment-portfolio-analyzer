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

    def __get_historical_data(self, symbol_or_symbols):
        response_df = self.clientStockAnalysis.get_historical_data(
            symbol_or_symbols=symbol_or_symbols,
            start=self.start_date,
            end=self.end_date,
            timeframe=self.timeframe,
            currency=self.currency,
        )
        return response_df

    def __average_daily_return(self, symbol_or_symbols):
        results = {}
        stock_data = self.__get_historical_data(symbol_or_symbols=symbol_or_symbols)
        daily_ret = stock_data.groupby("symbol")["close"].pct_change()
        mean = daily_ret.groupby("symbol").mean().to_dict()
        print(daily_ret.to_frame())
        print(daily_ret.groupby("symbol").std())
        standard_deviation = daily_ret.groupby("symbol").std().to_dict()
        return {"mean" : mean, "std" : standard_deviation}

    def expected_daily_portfolio_return(self):
        client_portfolio = PortfolioManager(api_key=api_key, api_secret=api_secret)
        position_weights = client_portfolio.weights_of_positions()
        symbol_or_symbols = []
        for pos in position_weights:
            symbol_or_symbols.append(pos)
        average_daily_returns = self.__average_daily_return(
            symbol_or_symbols=symbol_or_symbols
        )
        weighted_mean_daily_returns = {
            k: position_weights[k] * average_daily_returns["mean"][k]
            for k in position_weights
        }

        weighted_std_daily_returns = {
            k: pow(position_weights[k], 2) * pow(average_daily_returns["std"][k], 2)
            for k in position_weights
        }
        sum1= sum(weighted_std_daily_returns.values())

        sum_weighted_mean = sum(weighted_mean_daily_returns.values())
        sum_weighted_std = sqrt(sum(weighted_std_daily_returns.values())).real # sum weighted standard deviation

        return {
            "mean": sum_weighted_mean,
            "std": sum_weighted_std,
        }

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

    def calculate_sharpe_ratio(self, risk_rate: Optional[float] = None):
        if risk_rate is None:
            risk_rate = self.__fetch_risk_free_rate()
        portfolio_returns = self.expected_daily_portfolio_return()
        daily_risk_rate = risk_rate/(100*252)
        excess_returns = portfolio_returns["mean"] - daily_risk_rate
        print(excess_returns)
        sharpe_ratio = excess_returns / portfolio_returns["std"]
        return sharpe_ratio

if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("APCA_KEY")
    api_secret = os.getenv("APCA_SECRET")
    # You need to provide required arguments for AnalysisManager initialization
    # For demonstration, using example values for missing arguments
    symbols = "AAPL"  # Example symbol list
    today = date.today()
    five_years_ago = today - timedelta(weeks=520)
    today = today.strftime("%Y-%m-%d")
    five_years_ago = five_years_ago.strftime("%Y-%m-%d")
    client = AnalysisManager(
        api_key=api_key,
        api_secret=api_secret,
        start=five_years_ago,
        end=today,
    )
    print(client.calculate_sharpe_ratio())
