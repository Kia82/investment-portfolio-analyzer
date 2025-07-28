from cmath import sqrt
import pandas as pd
from api.simple_stat_calculations import SimpleStatCalculations
import montecarlo

class MonteCarloManager():
    
    def _calculate_stats(historical_positions_data: pd.DataFrame):
        simple_stat_calculation = SimpleStatCalculations(historical_positions_data=historical_positions_data)
        mean = simple_stat_calculation.calculate_mean()
        std = simple_stat_calculation.calculate_std()
        return {'mean': mean, 'std': std}
    
    def prepare_and_run_sim(principal, years, simulations, position_weights, historical_positions_data):
        stats = MonteCarloManager._calculate_stats(historical_positions_data=historical_positions_data)
        portfolio_avg_annual_return = 0
        portfolio_annual_volatility = 0
        for k in position_weights:
            print(stats)
            portfolio_avg_annual_return += position_weights[k] * stats['mean'][k] * 252
            # σₚ = sqrt( Σ (wᵢ² × σᵢ²) 
            # wᵢ = weight of asset i
            # σᵢ = std deviation of asset i
            portfolio_annual_volatility += sqrt(pow(position_weights[k], 2) * pow(stats['std'][k], 2)) * sqrt(252)
            portfolio_annual_volatility = portfolio_annual_volatility.real
        return montecarlo.runSimulation(float(principal), float(portfolio_avg_annual_return), float(portfolio_annual_volatility), int(years), int(simulations))
    

