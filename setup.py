"""Setup for rdiffb."""
from setuptools import setup, Command
import os
# setuptools used instead of distutils.core so that
# dependencies can be handled automatically

# Extract version number
import re
VERSIONFILE = "mdmux/__init__.py"
verfilestr = open(VERSIONFILE, "rt").read()
match = re.search(
    r"^__version__ = '(\d\.\d.\d+(\.\d+)?)'",
    verfilestr,
    re.MULTILINE)
if match:
    version = match.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE))


class Coverage(Command):
    """Class to allow coverage run from setup."""

    description = "run coverage"
    user_options = []

    def initialize_options(self):
        """Empty initialize_options."""
        pass

    def finalize_options(self):
        """Empty finalize_options."""
        pass

    def run(self):
        """Run coverage program."""
        os.system("coverage run --source=mdmux setup.py test")
        os.system("coverage report")
        os.system("coverage html")
        print("See htmlcov/index.html for details.")

setup(
    name='mdmux',
    version=version,
    packages=['mdmux'],
    scripts=['bf2marc.py', 'marcdiff.py'],
    classifiers=["Development Status :: 4 - Beta",
                 "Intended Audience :: Developers",
                 "License :: OSI Approved :: Apache Software License",
                 "Operating System :: OS Independent",  # is this true? know Linux & OS X ok
                 "Programming Language :: Python",
                 "Programming Language :: Python :: 2.7",
                 "Programming Language :: Python :: 3.4",
                 "Programming Language :: Python :: 3.5",
                 "Programming Language :: Python :: 3.6",
                 "Topic :: Software Development :: Libraries :: Python Modules"],
    author='Simeon Warner',
    author_email='simeon.warner@cornell.edu',
    description='mdmux',
    long_description=open('README').read(),
    url='http://github.com/zimeon/mdmux',
    install_requires=[
        "rdflib>=4.2.0",
        "pyld",
        "pymarc",
        "testfixtures",
        "rdflib-pyld-compat"
    ],
    test_suite="tests",
    cmdclass={
        'coverage': Coverage,
    },
)
