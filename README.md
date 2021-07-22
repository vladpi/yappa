# Simple deploy of python web-apps @YandexCloud

Forget about setting up your own infrastructure, vps, network, 
orchestrators, etc... go **serverless**

# Quickstart

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

### updates

when your code is updated just run

```shell
$ yappa deploy
 ```

# Deployment examples

Both WSGI and ASGI applications are supported (as well as raw functions). 
So Django, Flask, FastAPI... etc could be easily deployed.

Furthermore, not just regular json API could be deployed this way. 
Several types of applications could be launched with Yappa:

- [raw serverless function](https://github.com/turokg/yappa/tree/master/examples/raw_function)
- json API ([Flask](https://github.com/turokg/yappa/tree/master/examples/flask), 
  [FastAPI](https://github.com/turokg/yappa/tree/master/examples/fastapi), 
  Django rest framework)
- regular Django app
- single page application
- SPA + multiple API versions  
  ...   
  more examples will be added soon
# Django 
## management commands
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
environment variables. And then run 
```shell
$ yappa manage createsuperuser
```
The other way around would be to implement custom management command (see 
[StackOverflow topic](https://stackoverflow.com/questions/6244382/how-to-automate-createsuperuser-on-django))

# Yandex Cloud authorization
Command '$ yappa setup' prompts you for OAuth token. Then,
Yappa creates service account "yappa-uploader-service" with 
roles editor and serverless.functions.admin for the specified folder.
Key for this account is created and saved locally at .yc file.

Command '$ yappa deploy' supports two types of authorization

- service account key saved at .yc file (generated during '$ yappa setup')
- environment variables YC_OAUTH and YC_FOLDER

# Troubleshooting

- installing grpcio on M1 Apple M1  
  installing with anaconda may help. Also look
  at [stackoverflow](https://stackoverflow.com/questions/66640705/how-can-i-install-grpcio-on-an-apple-m1-silicon-laptop)

# Limitations
There are some limitations, however YandexCloud team is constantly releasing the
features and services. Also, this project will try to keep up. So stay tuned :)

## Database connectivity

Only YandexDB is supported inside Yandex Cloud. So any database you use has to have public IP address    

Managed Postgress will be added soon, see updates

## Headers and authorization

Please note that some request headers (like Authorization) are deleted before function is invoked

# Roadmap

Lots of features are on the way :)  
Listed order may not be the chronological order of implementation.
However, it's up to you, welcome to our  [telegram chat](https://t.me/yappa_chat)

### pre-release 
- pretty flask example app
- demo gif 
- habr article
- tests for POST calls to gw and function 
- refactor tests: make integration tests for all apps. make it uniform 
----
- Django support
    - management commands call
      - try if it's working
      - (+ creating of super user)
    - postgres support
    - support of S3 storage
- Improvements in CLI
    - env variables at deploy command
    - undeploy command
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
    - delete s3 key after deploy
    - avoiding s3 or avoiding reinstalling of all pip packages
    - cli logs command
    - why flask.app not working, fix it

### faraway plans

- health checks and revert policy
- celery support
- django: ydb orm support

# Support and contribution

Feel free to make pull request or ask anything at [telegram chat](https://t.me/yappa_chat)    
Also looking for contributors %)

# Acknowledgements

- [Mikhail Novikov](https://github.com/kurtgn) for starting this project two years ago
- [httpx](https://github.com/encode/httpx) as a great tool for calling WSGI/ASGI apps offline 
- [Zappa](https://github.com/Miserlou/Zappa) for inspiration  
