from alpaca_api import AlpacaStockHistoricalDataClient
from dotenv import load_dotenv
from alpaca.data.timeframe import TimeFrame
from datetime import datetime
from alpaca.common.enums import SupportedCurrencies
import pandas as pd
import os

class AnalysisManager:

# To analyze stock, user needs to initialize their symbols, start/end at minimum
    def __init__(
        self, 
        api_key, 
        api_secret, 
        symbol_symbols, 
        start, 
        end, 
        timeframe=TimeFrame.Day,
        currency=SupportedCurrencies.USD,
    ):
        self.client = AlpacaStockHistoricalDataClient(
            api_key=api_key, api_secret=api_secret
        )
        self.symbol_symbols = symbol_symbols
        self.start = start
        self.end = end
        self.timeframe = timeframe
        self.currency = currency

    def __calculate_daily_return(dataFrame: pd.DataFrame):
        daily_ret_table = dataFrame[['close']]
        daily_ret_table['daily_return'] = daily_ret_table['close'].pct_change()
        return daily_ret_table

    def get_historical_data(self):
        response_df = self.client.get_historical_data(
            symbol_or_symbols=self.symbol_or_symbols,
            start=self.start,
            end=self.end,
            timeframe=self.timeframe,
            currency=self.currency,
        )
        
        return response_df
    
    def calculate_sharpe_ratio(self):
        # TODO: Implement Sharpe ratio calculation
        pass


if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("APCA_KEY")
    api_secret = os.getenv("APCA_SECRET")
    # You need to provide required arguments for AnalysisManager initialization
    # For demonstration, using example values for missing arguments
    symbol_symbols = ["AAPL"]  # Example symbol list
    start = "2023-01-01"
    end = "2023-12-31"
    client = AnalysisManager(
        api_key=api_key,
        api_secret=api_secret,
        symbol_symbols=symbol_symbols,
        start=start,
        end=end
    )
    print(
        client.get_historical_data()
    )