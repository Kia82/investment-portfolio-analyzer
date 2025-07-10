from alpaca_api import AlpacaStockHistoricalDataClient
from dotenv import load_dotenv
from alpaca.data.timeframe import TimeFrame
from datetime import datetime
from alpaca.common.enums import SupportedCurrencies
import os

class AnalysisManager:

    def __init__(self, api_key, api_secret):
        self.client = AlpacaStockHistoricalDataClient(
            api_key=api_key, api_secret=api_secret
        )

    def get_historical_data(self, symbol_or_symbols, start, end, timeframe=TimeFrame.Day, currency=SupportedCurrencies.USD):
        response = self.client.get_historical_data(
            symbol_or_symbols=symbol_or_symbols,
            start=start,
            end=end,
            timeframe=timeframe,
            currency=currency
        )
        
if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("APCA_KEY")
    api_secret = os.getenv("APCA_SECRET")
    client = AnalysisManager(api_key=api_key, api_secret=api_secret)
    print(client.get_historical_data(symbol_or_symbols="SPY", 
                                     start=datetime(2025,6,30),
                                     end=datetime(2025,7,10),
                                     currency=SupportedCurrencies.CAD))