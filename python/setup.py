from setuptools import setup, find_packages
from pathlib import Path

VERSION = '0.1.0'
DESCRIPTION = 'randomowo python snippets'
AUTHOR = 'randomowo'
PYTHON_REQUIRES = '>=3.9.0'
REPO_URL = 'https://github.com/randomowo/snippets'

try:
    with open(Path(__file__).parent.joinpath('README.md')) as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

PACKAGE_DATA = {}

PACKAGES = find_packages(
    where='.',
    exclude=[],
)

REQUIRED = []

setup(
    name='randomowo_snippets',
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    author=AUTHOR,
    python_requires=PYTHON_REQUIRES,
    url=REPO_URL,
    include_package_data=False,
    package_data=PACKAGE_DATA,
    packages=PACKAGES,
    install_requires=REQUIRED,
)

