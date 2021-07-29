""" For installing package. See LICENSE
"""
from setuptools import setup, find_packages


def load_description():
    """Return description"""
    with open("README.md") as buffer:
        return buffer.read()


def load_version():
    """Return the version number"""
    with open("data_science_tools/__version__") as buffer:
        return buffer.readline().strip()


setup(
    name="data_science_tools",
    version=load_version(),
    author="Dylan Gregersen",
    author_email="an.email0101@gmail.com",
    url="https://github.com/earthastronaut/data_science_tools",
    license="MIT",
    description="Various tools useful for data science work",
    long_description=load_description(),
    python_requires=">=3.6",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        # For data manipulation.
        "pandas >= 0.23.4",
    ],
    extras_require={
        "matplotlib": [
            "matplotlib >= 3.2.1",
            "seaborn>=0.10.1",
        ],
        "plotly": [
            "plotly>=4.10.0",
            # kaleido==0.1.0,
        ],
    },
    classifiers=[
        "Intended Audience :: Data Science",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
)
