# Deployment of base Django DRF project
Here we will start new django project from scratch.
Then deploy and setup at Yandex cloud.

Only recently connection to Postgres from serverless
function has been added by Yandex CLoud (it's now in 
Preview). Currently it's not supported by Yappa.

Stay tuned, it will be ready in a couple of weeks. 
Hopefully by the end of july.


* [Start new project](#start-new-project)
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

set up DRF, paste this lines of code to the end of settings.py:

```python
DEBUG = False
INSTALLED_APPS += ['rest_framework']
REST_FRAMEWORK = {'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer', ]}
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3',
                         'NAME': Path("/tmp") / 'db.sqlite3', }}
```

add sample view to exmple_app/views.py

```python
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view()
def root(request):
    return Response({"message": "Hello, from Yappa!"})
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
./manage.py runserver
```

go to http://localhost:8000/

## Deploy 
Change env variables at yappa.yaml DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_PASSWORD, DJANGO_SUPERUSER_EMAIL

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