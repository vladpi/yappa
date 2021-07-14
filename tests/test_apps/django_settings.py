from pathlib import Path

from django.core.wsgi import get_wsgi_application
from django.http import HttpResponse
from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def main(request):
    return HttpResponse("root url")


@api_view(["GET"])
def json(request):
    return Response({
        "result": "json",
        "sub_result": {"sub": "json"}
    })


@api_view(["GET"])
def query_params(request):
    return Response({"params": request.query_params})


@api_view(["GET"])
def url_param(request, param):
    return Response({"param": param})


@api_view(["POST"])
def post(request):
    return Response({"request": request.data})


urlpatterns = [
    path('', main),
    path('json', json),
    path('query_params', query_params),
    path('url_param/<param>', url_param),
    path('post', post)
]

BASE_DIR = Path(__file__).resolve().parent
ROOT_URLCONF = 'django_settings'
SECRET_KEY = '^)qfu_0%x)ngcm!*7hs_d*myvfo0chk2kwk8yh'
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
]

