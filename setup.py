#!/usr/bin/env python
# -*- coding: utf-8 -*-
# setup.py
"""Setup script for project 'buchhaltung'."""

from setuptools import find_packages, setup  # type: ignore

with open("README.rst") as readme_file:
    long_description = readme_file.read()

requirements = [
    "gender-guesser",
    "prettytable",
    "wcwidth",
]

setup_requirements = [
    "pytest-runner",
]

test_requirements = [
    "pytest>=3",
]

setup(
    author="Oliver Stapel",
    author_email="hardy.ecc95@gmail.com",
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
        "Operating System :: POSIX :: Linux",
        "Topic :: Office/Business :: Financial :: Accounting",
    ],
    description="A text-based application to reproduce business transactions.",  # noqa
    install_requires=requirements,
    license="MIT license",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    include_package_data=True,
    keywords="accounting, erp",
    name="buchhaltung",
    packages=find_packages(exclude=("tests",)),  # noqa
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/0LL13/buchhaltung",
    version="0.0.13",
    zip_safe=False,
    extras_require={
        "dev": ["check-manifest"],
        "test": ["coverage"],
    },
    project_urls={
        "Bug Reports": "https://github.com/0LL13/buchhaltung/issues",
        "Source": "https://github.com/0LL13/buchhaltung",
    },
)
