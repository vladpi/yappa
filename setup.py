from setuptools import find_packages, setup

setup(
    name='yappa',
    version='0.5.00',
    description='',
    long_description=None,
    author='ek',
    author_email='kbkor@yandex.ru',  # mikhail.g.novikov@gmail.com
    packages=find_packages(), install_requires=[
        'boto3>=1.9', 'click>=7.0', 'python-slugify>=3.0'
    ],
    entry_points={'console_scripts': ['yappa = yappa.cli:cli']},
)
