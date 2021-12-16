#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages
from pathlib import Path

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()


# Read the requirements
source_root = Path(".")
with (source_root / "requirements.txt").open(encoding="utf8") as f:
    requirements = f.readlines()

test_requirements = ['pytest>=3', ]

setup(
    author="Alexandra Kapp",
    author_email='alexandra.kapp@htw-berlin.de',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Python Boilerplate contains all the boilerplate you need to create a Python package.",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='dp_mobility_report',
    name='dp-mobility-report',
    packages=find_packages(include=['dp_mobility_report', 'dp_mobility_report.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/FreeMoveProject/dp_mobility_report',
    version='0.0.1',
    zip_safe=False,
)