import pandas as pd

class SimpleStatCalculations():

    def __init__(self, historical_positions_data: pd.DataFrame):
        self.grouped_data = historical_positions_data.groupby('symbol')['close'].pct_change().dropna()

    def calculate_mean(self):
        mean = self.grouped_data.groupby("symbol").mean().to_dict()
        return mean
    
    def calculate_std(self):
        standard_deviation = self.grouped_data.groupby("symbol").std().to_dict()
        return standard_deviation
