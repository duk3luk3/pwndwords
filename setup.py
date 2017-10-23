#!/usr/bin/env python

from setuptools import setup

from pip.req import parse_requirements

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements(requirements.txt)

# reqs is a list of requirement
# e.g. ['django==1.5.1', 'mezzanine==1.4.6']
reqs = [str(ir.req) for ir in install_reqs]


setup(
    name="pwndwords",
    version="0.0.0",
    description="Pwnd Passwords API",
    long_description=open('README.txt').read(),
    author="Lukas Erlacher",
    author_email="erlacher@in.tum.de",
    url="http://github.com/duk3luk3/pwndwords",

    install_requires = reqs
    )
