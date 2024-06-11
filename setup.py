#!/usr/bin/env python
from setuptools import find_packages, setup


project = "microcosm-logging"
version = "2.0.0"

setup(
    name=project,
    version=version,
    description="Opinionated logging configuration",
    author="Globality Engineering",
    author_email="engineering@globality.com",
    url="https://github.com/globality-corp/microcosm-logging",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.6",
    keywords="microcosm",
    install_requires=[
        "loggly-python-handler>=1.0.0",
        "microcosm>=4.0.0",
        "python-json-logger>=0.1.9",
        "requests[security]>=2.18.4",
        "python-logstash-async>=2.3.0",
    ],
    setup_requires=[
    ],
    dependency_links=[
    ],
    entry_points={
        "microcosm.factories": [
            "logger = microcosm_logging.factories:configure_logger",
            "logging = microcosm_logging.factories:configure_logging"
        ],
    },
    extras_require={
        "test": [
            "coverage>=3.7.1",
            "parameterized>=0.8.1",
            "PyHamcrest>=1.9.0",
            "pytest-cov>=5.0.0",
            "pytest>=8.2.2",
        ],
    },
    tests_require=[
        "coverage>=3.7.1",
        "PyHamcrest>=1.9.0",
        "pytest-cov>=5.0.0",
    ],
)
