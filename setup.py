from setuptools import setup, Extension
import pybind11

ext_modules = [
    Extension(
        name="montecarlo",
        sources=["app/cpp/montecarlo.cpp"],
        include_dirs=[pybind11.get_include()],
    )
]

setup(
    name="montecarlo",
    version="0.0.1",
    ext_modules=ext_modules
)