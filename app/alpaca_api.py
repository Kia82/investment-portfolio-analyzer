
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
    def __init__(self, api_key, api_secret, paper=True):
        self.trading_client = TradingClient(api_key=api_key,secret_key=api_secret, paper=paper)
    
    def get_account(self):
        self.trading_client.get_account()
    
    def get_all_open_positions(self):
        self.trading_client.get_all_positions