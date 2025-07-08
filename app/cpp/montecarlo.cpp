#include <iostream>
#include <vector>
#include <boost/random.hpp>
#include <boost/accumulators/accumulators.hpp>
#include <boost/accumulators/statistics/mean.hpp>
#include <boost/accumulators/statistics/variance.hpp>
#include <boost/accumulators/statistics/p_square_quantile.hpp>
#include <pybind11/pybind11.h>

using namespace boost::accumulators;

struct Result {
    double meanPortfolioValue;
    double variance;
    double pSquareQuantile;
};

Result runSimulation(double principal, double meanReturn, double annualVolatility, int years, int simulations) {
    boost::mt19937 rng(static_cast<unsigned int>(std::time(0)));
    boost::random::normal_distribution<> norm_dist(meanReturn, annualVolatility);
    boost::variate_generator<boost::mt19937&, boost::random::normal_distribution<>> rand_return(rng, norm_dist);

    accumulator_set<double, features<tag::mean, tag::variance, tag::p_square_quantile>> acc(quantile_probability = 0.05);
    for (int i = 0; i< simulations; i++) {
        double value = principal;
        for(int y = 0; y < years; y++) {
            double yearly_return = rand_return();
            value *= (1.0 + yearly_return);
        }
        acc(value);
    }

    Result res;
    res.meanPortfolioValue = mean(acc);
    res.variance = variance(acc);
    res.pSquareQuantile = p_square_quantile(acc);
    return res;

}

// test function to ensure no import issues are taken place 
double add(double a, double b) {
    return a + b;
}

PYBIND11_MODULE(montecarlo, m) {
    m.def("runSimulation", &runSimulation, "Runs a monte carlo simulation with supplied parameters");
    m.def("add", &add, "A function that adds two numbers");
}