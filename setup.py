#!/usr/bin/env python

from codecs import open
from os import path

from setuptools import find_packages, setup

requirements = [
    "pandas>=1.0",
    "google-api-python-client>=2.0",
    "joblib>=1.0",
    "openpyxl>=3.0",
]
test_requirements = ["pytest"]

here = path.abspath(path.dirname(__file__))
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    author="Horatiu Bota",
    author_email="52171232+horatiubota@users.noreply.github.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.8",
    ],
    description="pgdrive lets you read and write DataFrames from and to Google Drive.",
    install_requires=requirements,
    license="MIT license",
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords="pandas,google,drive",
    name="pgdrive",
    packages=find_packages(include=["src"]),
    python_requires=">=3.8",
    tests_require=test_requirements,
    url="https://github.com/horatiubota/pgdrive",
    version="0.0.0",
    zip_safe=False,
)
