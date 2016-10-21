import os
from os.path import abspath, dirname, join
from setuptools import setup

__version__ = None
exec(open("ripe/atlas/tools/version.py").read())

# Allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

# Get proper long description for package
current_dir = dirname(abspath(__file__))
description = open(join(current_dir, "README.rst")).read()
changes = open(join(current_dir, "CHANGES.rst")).read()
long_description = '\n\n'.join([description, changes])

# Get the long description from README.md
setup(
    name="ripe.atlas.tools",
    version=__version__,
    packages=["ripe", "ripe.atlas", "ripe.atlas.tools"],
    namespace_packages=["ripe", "ripe.atlas"],
    include_package_data=True,
    license="GPLv3",
    description="The official command line client for RIPE Atlas",
    long_description=long_description,
    url="https://github.com/RIPE-NCC/ripe-atlas-tools",
    download_url="https://github.com/RIPE-NCC/ripe-atlas-tools",
    author="The RIPE Atlas team",
    author_email="atlas@ripe.net",
    maintainer="The RIPE Atlas team",
    maintainer_email="atlas@ripe.net",
    install_requires=[
        "IPy",
        "python-dateutil",
        "requests>=2.7.0",
        "ripe.atlas.cousteau==1.3",
        "ripe.atlas.sagan==1.1.11",
        "tzlocal",
        "pyyaml",
        "pyOpenSSL>=0.13",
    ],
    tests_require=[
        "nose",
        "coverage",
        "mock",
    ],
    extras_require={
        "doc": ["sphinx", "sphinx_rtd_theme"],
        "fast": ["ujson"],
    },
    test_suite="nose.collector",
    scripts=[
        "scripts/aping",
        "scripts/atraceroute",
        "scripts/adig",
        "scripts/asslcert",
        "scripts/ahttp",
        "scripts/antp",
        "scripts/ripe-atlas",
    ],
    keywords=['RIPE', 'RIPE NCC', 'RIPE Atlas', 'Command Line'],
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Internet :: WWW/HTTP",
    ],
)
