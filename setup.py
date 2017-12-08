"""Flying Circus network management NG"""

from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

_test_reqs = ['pytest', 'pytest-cov', 'pytest-flake8']

setup(
    name='fc-network',
    version='0.1',
    description=__doc__,
    long_description=long_description,
    url='https://flyingcircus.io',
    author='Christian Kauhaus',
    author_email='kc@flyingcircus.io',
    license='ZPL-2.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: System Administrators',
        'Topic :: System :: Networking',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python :: 3.4',
    ],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    setup_requires=['pytest-runner'],
    install_requires=[
        'click>=6',
        'colorama>=0.3',
        'Jinja2>=2.7',
        'orderedset>=2.0',
        'py>=1.4',
    ],
    extras_require={
        'dev': _test_reqs + ['check-manifest'],
        'test': _test_reqs,
    },
    tests_require=_test_reqs,
    package_data={'fc-network': []},
    entry_points={
        'console_scripts': [
            'fc-network=fc.network.main:main',
        ],
    },
)
