from setuptools import find_packages, setup
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

# Setup configuration
setup(
    name="investment-portfolio-analyzer",
    version="0.1",
    packages=find_packages("app"),  # assumes your packages live inside /app
    package_dir={"": "app"},  # tells setuptools to treat 'app' as the root
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    install_requires=[
        "alpaca-py",
        "pandas",
        "python-dotenv",
        "numpy",
        "alpaca-py",
        "pybind11"
    ],
    # zip_safe=False,
)