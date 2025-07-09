from alpaca_api import AlpacaClient
from dotenv import load_dotenv
from dataclasses import dataclass
import os

load_dotenv()

@dataclass
class Position:
    symbol: str
    quantity: float
    avg_entry_price: float
    current_price: float

def import_portfolio_from_alpaca():
    """
    Imports the current portfolio positions using the Alpaca API.
    Each position is converted into a Position object with relevant attributes (symbol, quantity, average entry price, and current price)
    and returned as a list.
    Returns:
        List[Position]: A list of Position objects representing the current portfolio holdings.
    Raises:
        EnvironmentError: If the required Alpaca API credentials are not set in environment variables.
        Exception: If there is an error communicating with the Alpaca API.
    """
    api_key = os.getenv("APCA_KEY")
    api_secret = os.getenv("APCA_SECRET")
    client = AlpacaClient(api_key=api_key, api_secret=api_secret)
    positions = client.get_all_positions()
    filtered_position = []
    for pos in positions:
        position = Position(
            symbol= pos.symbol,
            quantity= float(pos.qty),
            avg_entry_price =float(pos.avg_entry_price),
            current_price = float(pos.current_price)
        )
        filtered_position.append(position)
        
    return filtered_position


if __name__ == "__main__":
    import_portfolio_from_alpaca()