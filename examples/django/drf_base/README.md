# Setting up project
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
REST_FRAMEWORK = {
        'DEFAULT_RENDERER_CLASSES': [
                'rest_framework.renderers.JSONRenderer',
                ]
        }
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