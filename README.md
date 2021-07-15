# Simple serverless deploy of python web-apps @YandexCloud

Forget about setting up your own infrastructure, vps, network, 
orchestrators, etc...

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

Not just regular json API could be deployed this way. Several types of applications could be deployed with Yappa:

- raw serverless function
- json API (Flask, Django rest framework)
- regular Django app
- single page application
- SPA + multiple API versions  
  ...   
  see examples folder

# Yandex Cloud authorization

Command '$ yappa deploy' supports two types of authorization at YandecCloud

- service account key saved at .yc file (generated during '$ yappa setup')
- environment variables (YC_OAUTH and YC_FOLDER variables should be set)

# Troubleshooting

- installing grpcio on M1 Apple M1  
  installing with anaconda may help. Also look
  at [stackoverflow](https://stackoverflow.com/questions/66640705/how-can-i-install-grpcio-on-an-apple-m1-silicon-laptop)

# Limitations

## Frameworks support

At this point WSGI applications and raw functions are supported, tested on Flask and Django. ASGI applications (FastAPI,
Starlette) will be added in the future

## Database connectivity

Only YandexDB is supported inside Yandex Cloud. So any database you use has to have public IP address    
Managed Postgress will be added soon, see updates

## Headers and authorization

Please note that some request headers (like Authorization) are deleted before function is invoked

# Roadmap

Lots of features are on the way :)  
Listed order may not be the chronological order of implementation.
However, it's up to you, welcome to our  [telegram chat](https://t.me/yappa_chat)

- Support of asgi app
- Django support
    - management commands call
    - postgres support
    - support of S3 storage
- Improvements in CLI
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
        - SPA + DRF + authorisation
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
- [httpx](https://github.com/encode/httpx) as a great tool for calling WSGI/ASGI apps
- [Zappa](https://github.com/Miserlou/Zappa) for inspiration  
