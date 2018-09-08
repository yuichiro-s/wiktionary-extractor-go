from distutils.core import setup

from setuptools import find_packages

setup(
    name='wiktionary_extractor',
    version='0.0.1',
    description='Create dictionary data from rendered Wiktionary pages',
    packages=find_packages(),
    requires=[
        'bs4',
    ])
