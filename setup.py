from setuptools import setup, find_packages

setup(
    name="japan-stock-predict",
    version="1.0.0",
    description="Japan Stock Market Prediction Engine (DuckDB + Arrow + SaC + Mojo + Chapel + PyMC + Z3 SMT)",
    author="Prediction Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "duckdb>=1.0.0",
        "pyarrow>=15.0.0",
        "pymc>=6.0.0",
        "z3-solver>=4.12.0",
        "numpy>=1.24.0",
        "psutil>=5.9.0"
    ],
    entry_points={
        "console_scripts": [
            "predict-japan=cli:main",
        ],
    },
    python_requires=">=3.10",
)
