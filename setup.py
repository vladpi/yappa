from setuptools import find_packages, setup

setup(
    name='yappa',
    version='0.5.00',
    description='Easy serverless deploy of python web applications',
    long_description="""
    - create account at Yandex Cloud
    - $yappa setup
    - $yappa deploy
    that's it!
    """,
    author='Egor Korovin',
    author_email='kbkor@yandex.ru',
    packages=find_packages(), install_requires=[
        'boto3>=1.9',
        'click>=7.0', 'python-slugify>=3.0'
    ],
    entry_points={'console_scripts': ['yappa = yappa.cli:cli']},
)
