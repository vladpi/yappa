<p align="center"><img src="logo.png" width="400"></p>


# Simple deploy of python web-apps @YandexCloud

Forget about setting up your own infrastructure, vps, network, 
orchestrators, etc... go **serverless**

<p align="center"><img src="demo.gif" width="720" ></p>

* [Quickstart](#quickstart)
    * [Updates](#updates)
* [Deployment examples](#deployment-examples)
* [Django](#django)
    * [Management commands](#management-commands)
    * [Creating superuser](#creating-superuser)
* [Yandex Cloud authorization](#yandex-cloud-authorization)
* [Limitations](#limitations)
    * [Database connectivity](#database-connectivity)
    * [Headers and authorization](#headers-and-authorization)
* [Roadmap](#roadmap)
    * [Next steps](#next-steps)
    * [Far-faraway plans](#far-faraway-plans)
* [Troubleshooting](#troubleshooting)
* [Support and contribution](#support-and-contribution)
* [Acknowledgements](#acknowledgements)

## Quickstart

1. setup virtual env, create your app
2. create account at Yandex Cloud
3. install Yappa

```shell
$ pip install yappa -U
$ pip freeze > requirements.txt
 ```

4. use Yappa:

```shell
$ yappa setup
$ yappa deploy
 ```

...that's it! Your application is deployed

### Updates

when your code is updated just run

```shell
$ yappa deploy
 ```

## Deployment examples

Both WSGI and ASGI applications are supported (as well as raw functions). 
So Django, Flask, FastAPI... etc could be easily deployed.

Furthermore, not just regular json API could be deployed this way. 
Several types of applications could be launched with Yappa:

- [raw serverless function](https://github.com/turokg/yappa/tree/master/examples/raw_function)
- json API ([Flask](https://github.com/turokg/yappa/tree/master/examples/flask), 
  [FastAPI](https://github.com/turokg/yappa/tree/master/examples/fast_api), 
  [Django rest framework](https://github.com/turokg/yappa/tree/master/examples/django/drf_base))
- regular Django app
- single page application
- SPA + multiple API versions  
  ...   
  more examples will be added soon
## Django 
### Management commands
django manage.py commands are supported. just run 
```shell
$ yappa manage migrate
```

In order to support management commands, for Django projects second
cloud function is being created every deploy. It's made only for handling
management commands, and it's not public. Therefore, commands do not 
support user inputs: to every command '--no-input' flag is added.

### Creating superuser 
As of Django 3.0 env variables are supported for createsuperuser command. So 
you should deploy your app with DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_PASSWORD 
environment variables. Then run 
```shell
$ yappa manage createsuperuser
```
The other way around would be to implement custom management command (see 
[StackOverflow topic](https://stackoverflow.com/questions/6244382/how-to-automate-createsuperuser-on-django))

## Yandex Cloud authorization
Command '$ yappa setup' prompts you for OAuth token. Then,
Yappa creates service account "yappa-uploader-service" with 
roles editor and serverless.functions.admin for the specified folder.
Key for this account is created and saved locally at .yc file.

Command '$ yappa deploy' supports two types of authorization

- service account key saved at .yc file (generated during '$ yappa setup')
- environment variables YC_OAUTH and YC_FOLDER

## Limitations
There are some limitations, however YandexCloud team is constantly releasing the
features and services. Also, the team of this project will try to keep up. So stay tuned :)

### Database connectivity

Only YandexDB is supported inside Yandex Cloud. So any database you use has to have public IP address    

Managed Postgress will be added soon, see updates

### Headers and authorization

Please note that some request headers (like Authorization) are 
[deleted before function is invoked](https://cloud.yandex.ru/docs/functions/concepts/function-invoke)

## Roadmap

Listed order may not be the chronological order of implementation.
However, it's up to you, welcome to our  [telegram chat](https://t.me/yappa_chat)

### Next steps
- Django support
    - postgres support
    - support of S3 storage
- Improvements in CLI
    - env variables at deploy command
    - validation of inputs at yappa setup
    - validation of requirements and entrypoint at yappa deploy
    - auto-suggestion of app path (trying to load asgi or wsgi app)
    - upload_to_bucket - add progress bar
- Error handling
    - no access
- Documentation
    - add deployment examples
        - pretty flask app
        - django + postgres
        - classic django with s3
        - SPA
        - SPA + DRF + authorization
        - SPA + two api versions
    - habr articles with deployment examples
    - habr article with full cycle of web-site (from code to domain)
- Random features
    - tests for POST calls to gw and function
    - refactor tests: make integration tests for all apps. make it uniform
    - delete s3 key after deploy
    - avoiding s3 or avoiding reinstalling of all pip packages
    - cli logs command
    - why flask.app not working, fix it

### Far-faraway plans

- health checks and revert policy
- celery support
- django: ydb orm support

## Troubleshooting

- installing grpcio on Apple M1: installing with anaconda may help. Also look
  at [stackoverflow](https://stackoverflow.com/questions/66640705/how-can-i-install-grpcio-on-an-apple-m1-silicon-laptop)

## Support and contribution

Feel free to make pull request or ask anything at [telegram chat](https://t.me/yappa_chat)    
Also looking for contributors %)

## Acknowledgements

- [Mikhail Novikov](https://github.com/kurtgn) for starting this project two years ago
- [httpx](https://github.com/encode/httpx) as a great tool for calling WSGI/ASGI apps offline 
- [Zappa](https://github.com/Miserlou/Zappa) for inspiration  
