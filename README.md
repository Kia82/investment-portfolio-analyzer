# Investment Portfolio Analyzer
A Python-based tool that helps users analyze and understand the performance and risk of their investment portfolios. 
It leverages financial APIs, SQL, and optional C++ modules for advanced computations.

🚀 Features
🧮 Performance Metrics: Calculates ROI, CAGR, and Sharpe Ratio

📈 Visualizations: Portfolio performance over time, asset allocation pie charts

💡 Diversification Analysis: Sector & asset-type breakdowns

📉 Risk Simulation: Monte Carlo simulation (written in C++ for speed)

🧠 Insights: Recommends rebalancing strategies and diversification tips

🗃️ Database Integration: Store and retrieve portfolios and transactions using SQL

🔐 Brokerage Integration: Fetch data from APIs like Alpaca or Wealthsimple

## Package Structure
```
investment-portfolio-analyzer/
│
├── app/
│   ├── __init__.py
│   ├── main.py              # Entry point (CLI or Streamlit app)
│   ├── portfolio.py         # Core portfolio logic
│   ├── analysis.py          # Financial computations & metrics
│   ├── visualization.py     # Plotting charts & graphs
│   ├── database.py          # SQL models and queries
│   └── config.py            # API keys, DB configs
│
├── cpp/
│   ├── montecarlo.cpp       # Risk analysis module (compiled)
│   └── CMakeLists.txt       # C++ build instructions
│
├── data/
│   └── example_portfolio.csv
│
├── tests/
│   └── test_analysis.py
│
├── requirements.txt
├── Dockerfile
├── .env
└── README.md
```

## Installation 
```py
# Clone and go into repo 
git clone https://github.com/Kia82/investment-portfolio-analyzer.git
cd investment-portfolio-analyzer

# Install dependencies
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Create database
python app/database.py --init

# Run app
python app/main.py

```


## Sample CLI Usage

```py

# Initialize 
python app/main.py --import data/example_portfolio.csv
python app/main.py --analyze
python app/main.py --visualize

```


