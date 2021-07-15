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
Not just regular json API could be deployed this way. Several types of
applications could be deployed with Yappa:
- json API (Flask, Django rest framework)
- regular Django app
- raw serverless function
- single page application 
- SPA + multiple API versions  
...   
see examples folder
# Roadmap
!TODO
# Support and contribution
Feel free to make pull request or ask anything at https://t.me/yappa_chat    
Also looking for contributors %)
# Limitations
## Frameworks support
At this point WSGI applications and raw functions are supported, 
tested on Flask and Django. ASGI applications (FastAPI, Starlette) will be added in the future
## Database connectivity
Only YandexDB is supported inside Yandex Cloud. So any database you use 
has to have public IP address    
Managed Postgress will be added soon, see updates
## Headers and authorization
Please note that some request headers (like Authorization) are deleted before function is invoked 
# How does this work
! TODO
# Yandex Cloud authorization 
! TODO
# Troubleshooting
- grpcio on Apple M1   
There is a known issue with installing grpcio on M1 Macs, 
  installing with anaconda may help. Also look at 
  https://stackoverflow.com/questions/66640705/how-can-i-install-grpcio-on-an-apple-m1-silicon-laptop
  

  
# Acknowledgements
! TODO