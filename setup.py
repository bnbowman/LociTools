
import sys

from setuptools import setup, find_packages

if ("install" in sys.argv) and sys.version_info < (2, 7, 0):
    raise SystemExit("LociTools requires Python 2.7")

__VERSION__ = "0.1.0"

DESC = 'Tools for analyzing complex HLA data from SMRT Sequencing'

scripts = [
    "bin/loci",
]

required = [
    "enum34 >= 1.1.6",
    "numpy >= 1.10.1",
    "pbcore >= 1.2.6",
]

setup(
    name = 'LociTools',
    version=__VERSION__,
    author='Brett Bowman',
    author_email='bbowman@pacificbiosciences.com',
    url='https://github.com/bnbowman/LociTools',
    description=DESC,
    license=open('LICENSES.txt').read(),
    packages = find_packages(),
    zip_safe = False,
    scripts = scripts,
    install_requires = required,
)
