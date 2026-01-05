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
    float meanPortfolioValue;
    float variance;
    float pSquareQuantile;
};

Result runSimulation(float principal, float meanReturn, float annualVolatility, int years, int simulations) {
    boost::mt19937 rng(static_cast<unsigned int>(std::time(0)));
    boost::random::normal_distribution<> norm_dist(meanReturn, annualVolatility);
    boost::variate_generator<boost::mt19937&, boost::random::normal_distribution<>> rand_return(rng, norm_dist);

    accumulator_set<float, features<tag::mean, tag::variance, tag::p_square_quantile>> acc(quantile_probability = 0.05);
    for (int i = 0; i< simulations; i++) {
        float value = principal;
        for(int y = 0; y < years; y++) {
            float yearly_return = rand_return();
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

// test function for easy debugging    
float add(float a, float b) {
    return a + b;
}

// PYBIND11_MODULE(montecarlo, m) {
//     pybind11::class_<Result>(m, "Result")
//         .def(pybind11::init<float, float, float>())
//         .def_readwrite("meanPortfolioValue", &Result::meanPortfolioValue)
//         .def_readwrite("variance", &Result::variance)
//         .def_readwrite("pSquareQuantile", &Result::pSquareQuantile);

//     m.def("runSimulation", &runSimulation, "Runs a monte carlo simulation with supplied parameters");
//     m.def("add", &add, "A function that adds two numbers");
// }

PYBIND11_MODULE(montecarlo, m) {
    m.doc() = "pybind11 example plugin";
    m.def("add", &add, "A function that adds two numbers", pybind11::arg("i"), pybind11::arg("j"));
}