import montecarlo
from portfolio import import_portfolio_from_alpaca

def main():
    positions = import_portfolio_from_alpaca()
    for pos in positions:
        print(pos)

if __name__ == "__main__":
    main()