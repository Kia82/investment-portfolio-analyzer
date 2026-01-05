from datetime import date, timedelta
import montecarlo
# from portfolio import import_portfolio_from_alpaca
from dotenv import load_dotenv
from analysis_manager import *
import os

def main():
    load_dotenv()
    api_key = os.getenv("APCA_KEY")
    api_secret = os.getenv("APCA_SECRET")
    today = date.today()
    ten_years_ago = today - timedelta(weeks=520)
    today_formatted = today.strftime("%Y-%m-%d")
    ten_years_ago_formatted = ten_years_ago.strftime("%Y-%m-%d")

    client = AnalysisManager(api_key=api_key,
                             api_secret=api_secret,
                             start=ten_years_ago_formatted,
                             end=today_formatted)
    
    print(client.calculate_sharpe_ratio())
    print(client.calculate_sortino_ratio())
    print(client.calculate_treynor_ratio())
    print(montecarlo.add(i=1,j=4))
    pass

if __name__ == "__main__":
    main()