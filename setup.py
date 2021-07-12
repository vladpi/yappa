from setuptools import find_packages, setup

setup(
    name='yappa',
    version='0.4.1',
    description='Easy serverless deploy of python web applications',
    long_description="""
# Simple and Easy serverless deploy of python web-apps Yandex Cloud
1. create account at Yandex Cloud
2. use Yappa:
```shell
$ yappa setup
$ yappa deploy
 ``` 
## that's it!
    """,
    author='Egor Korovin',
    author_email='kbkor@yandex.ru',
    packages=find_packages(),
    install_requires=[
        'boto3>=1.10',
        'click>=8.0',
        'httpx>=0.18',
        'yandexcloud>=0.92',
        'boltons>=21.0',
        'idna<3,>=2.5',
        "PyYAML>=5.0",
        "furl>=2.0",
        "pytz>=2021"
    ],
    python_requires='>3.8.0',
    entry_points={'console_scripts': ['yappa = yappa.cli:cli']},
)
