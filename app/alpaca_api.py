
# import os
# from dotenv import load_dotenv

# load_dotenv()
from alpaca.trading.client import TradingClient


# APCA_KEY = os.getenv("APCA_KEY")
# APCA_SECRET = os.getenv("APCA_SECRET")
# accept = "application/json"
# headers = {
#     "accept": accept,
#     "APCA-API-KEY-ID": APCA_KEY,
#     "APCA-API-SECRET-KEY": APCA_SECRET,
# }

# r = requests.get("https://paper-api.alpaca.markets/v2/account", headers=headers)
# print(r.json())


class AlpacaClient:
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
        self.trading_client = TradingClient(api_key=api_key,secret_key=api_secret, paper=paper)
    
    def get_account(self):
        self.trading_client.get_account()
    
    def get_orders(self, filter):
        self.trading_client.get_orders(filter=filter)

    def get_all_positions(self):
        return self.trading_client.get_all_positions()
    