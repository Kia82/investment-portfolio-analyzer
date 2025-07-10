from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension, build_ext

"""
For the purposes of setting up python binding (making cpp libraries useable in python) 
"""

ext_modules = [
    Pybind11Extension(
        "montecarlo",  # name of the module
        ["app/cpp/montecarlo.cpp"],  # your cpp file
    ),
]

setup(
    name="montecarlo",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
)