""" For installing package. See LICENSE
"""
import re
from setuptools import setup

SHORT_DESCRIPTION = "Various tools useful for data science work"
with open('README.md') as f:
    LONG_DESCRIPTION = f.read()


with open('./data_science_tools/__init__.py') as f:
    version = next(
        re.finditer(
            r'\n__version__ *= *[\'\"]([0-9\.]+)[\'\"]',
            f.read(),
        )
    ).groups()[0]


setup(
    name='data_science_tools',
    version=version,
    author='Dylan Gregersen',
    author_email='an.email0101@gmail.com',
    url='https://github.com/earthastronaut/data_science_tools',
    license='MIT',
    description=SHORT_DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    python_requires='>=3.6',
    install_requires=[
        "pandas >= 1.0.3",
        "matplotlib >= 3.2.1",
    ],
    classifiers=[
        'Intended Audience :: Data Sceince',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ]
)
