import os
from setuptools import setup

__version__ = None
exec(open("ripe/atlas/tools/version.py").read())

# Allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

# Get the long description from README.md
with open(os.path.join(os.path.dirname(__file__), "README.rst")) as description:
    setup(
        name="ripe.atlas.tools",
        version=__version__,
        packages=["ripe", "ripe.atlas", "ripe.atlas.tools"],
        namespace_packages=["ripe", "ripe.atlas"],
        include_package_data=True,
        license="GPLv3",
        description="The official command line client for RIPE Atlas",
        long_description=description.read(),
        url="https://github.com/RIPE-NCC/ripe-atlas-tools",
        download_url="https://github.com/RIPE-NCC/ripe-atlas-tools",
        author="The RIPE Atlas team",
        author_email="atlas@ripe.net",
        maintainer="The RIPE Atlas team",
        maintainer_email="atlas@ripe.net",
        install_requires=[
            "ripe.atlas.cousteau>=0.9.2",
            "ripe.atlas.sagan>=1.1.1",
            "tzlocal",
            "pyyaml",
        ],
        tests_require=["nose"],
        extras_require={
            "doc": ["sphinx"]
        },
        test_suite="nose.collector",
        scripts=[
            "scripts/ripe-atlas"
        ],
        classifiers=[
            "Operating System :: POSIX",
            "Operating System :: Unix",
            "Programming Language :: Python",
            "Programming Language :: Python :: 2.7",
            "Topic :: Internet :: WWW/HTTP",
        ],
    )
