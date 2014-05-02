import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "lsftools",
    version = "0.0.1",
    author = "Guy Haskin Fernald",
    author_email = "guy@guyhf.com",
    description = ("A set of tools to facilitate submitting and",
                   "monitoring jobs on a cluster using LSF."),
    license = "Apache Software",
    keywords = "LSF cluster job management",
    url = "http://packages.python.org/an_example_pypi_project",
    packages=['lsftools'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: Apache Software License",
    ],
    scripts = [
        'bin/hog',
        'bin/hogrun',
        'bin/wherejobs'
    ]
)
