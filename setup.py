#!/usr/bin/env python
from setuptools import find_packages, setup


project = "microcosm-logging"
version = "1.5.0"

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
        "microcosm>=2.0.0",
        "python-json-logger>=0.1.9",
        "requests[security]>=2.18.4",
    ],
    setup_requires=[
        "nose>=1.3.6",
    ],
    dependency_links=[
    ],
    entry_points={
        "microcosm.factories": [
            "logger = microcosm_logging.factories:configure_logger",
            "logging = microcosm_logging.factories:configure_logging"
        ],
    },
    tests_require=[
        "coverage>=3.7.1",
        "PyHamcrest>=1.9.0",
    ],
)
