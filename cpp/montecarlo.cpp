#include "montecarlo.h"

double runSimulation(double principal, double mean, double annualVolatility, int years, int numimulations) {
    // Implements the Monte Carlo simulation algorithm to estimate
    // investment growth over a specified number of years.
    //
    // For now, this function returns a simplified dummy result.
    return principal * (1 + mean / 100) * years;
}
