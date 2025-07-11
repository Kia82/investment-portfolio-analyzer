from datetime import datetime
from typing import Optional
from alpaca.trading.client import TradingClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.timeframe import TimeFrame
from alpaca.common.enums import SupportedCurrencies

class AlpacaTradingClient:
    """
    AlpacaClient provides a wrapper around the Alpaca TradingClient for interacting with the Alpaca API.
    Attributes:
        trading_client (TradingClient): An instance of the Alpaca TradingClient.
    Methods:
        __init__(api_key, api_secret, paper=True):
            Initializes the AlpacaClient with API credentials and environment.
        get_account():
            Retrieves account information from Alpaca.
        get_orders(filter):
            Retrieves orders from Alpaca, optionally filtered by the provided filter.
        get_all_positions():
            Retrieves all open positions from Alpaca.
    """

    def __init__(self, api_key, api_secret, paper=True):
        self.trading_client = TradingClient(
            api_key=api_key, secret_key=api_secret, paper=paper
        )

    def get_account(self):
        self.trading_client.get_account()

    def get_orders(self, filter):
        self.trading_client.get_orders(filter=filter)

    def get_all_positions(self):
        return self.trading_client.get_all_positions()


class AlpacaStockHistoricalDataClient:
    """
    A client for retrieving historical stock data using the Alpaca API.
    This class provides a convenient interface to fetch historical bar data (such as OHLCV)
    for one or more stock symbols, supporting custom date ranges, result limits, currency selection, and sorting options.
    Args:
        api_key (str): The Alpaca API key.
        api_secret (str): The Alpaca API secret key.
    Methods:
        get_historical_data(
            currency: Optional[SupportedCurrencies] = None,
            Fetches historical bar data for the specified symbol(s).
            Args:
                symbol_or_symbols (str | list[str]): A single stock symbol or a list of symbols to retrieve data for.
                start (Optional[datetime]): The start datetime for the data range (inclusive). If None, uses API default.
                end (Optional[datetime]): The end datetime for the data range (exclusive). If None, uses API default.
                timeframe (TimeFrame): The time interval for each data point.
            Returns:
                The historical bar data as returned by the Alpaca API.
    """

    def __init__(self, api_key, api_secret):
        self.historical_data = StockHistoricalDataClient(
            api_key=api_key, secret_key=api_secret
        )

    def get_historical_data(
        self,
        symbol_or_symbols: str | list[str],
        start: Optional[datetime],
        end: Optional[datetime],
        timeframe: TimeFrame,
        currency: SupportedCurrencies
    ):
        request_params = StockBarsRequest(
            symbol_or_symbols=symbol_or_symbols,
            start=start,
            end=end,
            timeframe=timeframe,
            currency=currency
        )
        return self.historical_data.get_stock_bars(request_params=request_params).df


# class AlpacaClientFacade:
#     """
#     A facade class for interacting with Alpaca's trading and historical data APIs.

#     This class simplifies the initialization and usage of Alpaca's Trading and Historical Data clients.

#     Attributes:
#         trading (AlpacaTradingClient): The client for trading operations.
#         historical (AlpacaStockHistoricalDataClient): The client for accessing historical stock data.

#     Args:
#         api_key (str): The API key for Alpaca authentication.
#         api_secret (str): The API secret for Alpaca authentication.
#         paper (bool, optional): Whether to use the paper trading environment. Defaults to True.
#     """

#     def __init__(self, api_key, api_secret, paper=True):
#         self.trading = AlpacaTradingClient
#         self.historical = AlpacaStockHistoricalDataClient
