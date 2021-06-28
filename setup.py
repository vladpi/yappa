
from setuptools import find_packages, setup

setup(
    name='yappa',
    version='0.3.12',
    description='',
    long_description=None,
    author='Mike',
    author_email='mikhail.g.novikov@gmail.com',
    packages=find_packages(), install_requires=[
        'boto3>=1.9', 'click>=7.0', 'python-slugify>=3.0'
    ],
    entry_points= {'console_scripts': ['yappa = yappa.cli:cli']},
)

