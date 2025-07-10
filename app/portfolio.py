from alpaca_api import AlpacaTradingClient
from dotenv import load_dotenv
from dataclasses import dataclass
import os


@dataclass
class Position:
    symbol: str
    quantity: float
    avg_entry_price: float
    current_price: float


class PortfolioManager:

    def __init__(self, api_key, api_secret):
        self.client = AlpacaTradingClient(api_key=api_key, api_secret=api_secret)

    def import_portfolio_from_alpaca(self):
        """
        Imports the current portfolio positions using the Alpaca API. Each position is converted into a Position object with relevant attributes
        (symbol, quantity, average entry price, and current price) and returned as a list.

        Returns:
            List[Position]: A list of Position objects representing the current portfolio holdings.

        Raises:
            EnvironmentError: If the required Alpaca API credentials are not set in environment variables.
            Exception: If there is an error communicating with the Alpaca API.
        """

        positions = self.client.get_all_positions()
        filtered_positions = [
            Position(
                symbol=pos.symbol,
                quantity=float(pos.qty),
                avg_entry_price=float(pos.avg_entry_price),
                current_price=float(pos.current_price),
            )
            for pos in positions
        ]
        return filtered_positions

if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("APCA_KEY")
    api_secret = os.getenv("APCA_SECRET")
    manager = PortfolioManager(api_key, api_secret)
    print(manager.import_portfolio_from_alpaca())
