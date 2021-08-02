# Deployment of base Django DRF project
Here we will start new django project using managed PostgreSQL
from scratch. Then deploy and setup at Yandex cloud.

At this point (2nd aug 2021) serverless connection to Postgresql is
in Preview phase, so you have to ask for access through YandexCloud
console. 

* [Start new project](#start-new-project)
* [Prepare managed Postgres](#prepare-managed-postgres)
* [Deploy](#deploy)
* [Setup](#setup)
## Start new project

setup new virtual env

```shell
$ python3 -m venv venv 
$ source venv/bin/activate
$ pip install django djangorestframework yappa
$ pip freeze > requirements.txt
```

start blank Django project:

```shell
$ django startproject drf_base
$ cd drf_base
$ django startapp example_app
```

set up DRF, paste these lines of code to the end of settings.py:

```python
DEBUG = False
INSTALLED_APPS += ['rest_framework']
REST_FRAMEWORK = {'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer', ]}
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv("PG_CONNECTION_ID"),
        'USER': os.getenv("PG_USER"),
        'PASSWORD': os.getenv("IAM_TOKEN"),
        'HOST': os.getenv("PG_HOST"),
        'PORT': os.getenv("PG_PORT"),
        'OPTIONS': {'sslmode': 'require'},
    }
}
```

add sample view to exmple_app/views.py

```python 
from django.db import connection
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view()
def root(request):
  try:
    with connection.cursor() as cursor:
      cursor.execute("SELECT 42")
      result = cursor.fetchall()
    db_message = f"{result} - was fetched from PostgreSQL"
  except Exception as e:
    db_message = f"Couldn't connect to db ({e})"
  return Response({"message": "Hello, from Yappa!",
                   "message from db": db_message})
```

setup urls settings   
example_app/urls.py:

```python
from django.urls import path
from .views import root

urlpatterns = [path("", root), ]
```

drf_base/urls.py:

```python
from django.urls import include, path

urlpatterns = [path('', include('example_app.urls'))]
```

check that app is properly setup

```shell
./manage.py check
```

## Prepare managed Postgres
This is a step-by-step guide, which you can find at 
[YandexCloud docs](https://cloud.yandex.ru/docs/functions/operations/database-connection)

### 1. Create Postgres cluster 
First you should create managed Postgres cluster. Go to your 
folder at YandexCloud console and set it up :)

Don't forget to check "access from serverless" option in cluster settings
### 2. Create serverless connection 
Python app will not have access to db directly. It will use
[Odyssey connection manager](https://github.com/yandex/odyssey). 
So you should create connection from YandexCloud console 
(Folder -> Cloud Functions -> DB Connection). 

### 3. Create service account 
Create service account which will be associated with serverless 
function. 
- go to YandexCloud console, Folder -> Service Accounts 
- create service account 
- add permission 'serverless.mdbProxies.user'

### 4. Configure yappa.yaml 
(if you don't have yappa.yaml file yet, run $ yappa setup && yappa deploy)

- add superuser credentials (after you've created superuser you can
  save them elsewhere and delete from this file)
- PG_USER is property of Postgres cluster from 1st step
- PG_CONNECTION_ID, PG_HOST are properties of connection created on the 2nd step
- PG_PORT - 6432 is default for YandexCloud 
- service_account_id - is id of service account you've created on the 3rd step.

after that yappa.yaml file will look like this:
```yaml
...
environment:
  DJANGO_SUPERUSER_USERNAME: superuser
  DJANGO_SUPERUSER_PASSWORD: LOLiAMnot_secure!
  DJANGO_SUPERUSER_EMAIL: chang@me.com
  
  PG_USER: user1
  PG_CONNECTION_ID: akfrhhp29ipa93s294qd
  PG_HOST: akfrhhp29ipa93s294qd.postgresql-proxy.serverless.yandexcloud.net
  PG_PORT: '6432'
service_account_id: ajek47377f918mdmmqha
```

## Deploy 
Change env variables at yappa.yaml DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_PASSWORD, 
DJANGO_SUPERUSER_EMAIL

run
```shell
$ yappa setup 
$ yappa deploy 
```

## Setup 
run 
```shell
$ yappa manage migrate 
$ yappa manage createsuperuser
```
from this point superuser is created, so you can remove 
credentials from yappa.yaml