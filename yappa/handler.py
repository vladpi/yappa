import json
import os
from importlib import import_module

import httpx

CONFIG_FILENAME = "yappa.yaml"


def load_config(filename):
    pass


def load_app(import_path=None, django_settings_module=None):
    # TODO add delay, test if setup is done during setup, not when handling
    #  response
    if import_path:
        *submodules, app_name = import_path.split(".")
        module = import_module(".".join(submodules))
        app = getattr(module, app_name)
        return app
    if django_settings_module:
        from django.core.wsgi import get_wsgi_application
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", django_settings_module)
        import django
        if django.VERSION[0] <= 1 and django.VERSION[1] < 7:
            # call django.setup only for django <1.7.0
            # (because setup already in get_wsgi_application since that)
            # https://github.com/django/django/commit
            # /80d74097b4bd7186ad99b6d41d0ed90347a39b21
            django.setup()
        return get_wsgi_application()
    raise ValueError("either 'import_path' or 'django_settings_module'"
                     "params must be provided")


def patch_response(response):
    """
    returns Http response in the format of
    {
     'status code': 200,
     'body': body,
     'headers': {}
    }
    """
    return {
            'statusCode': response.status_code,
            'headers': response.headers,
            'body': response.content.decode(),
            }


def call_app(app, event):
    """
    call wsgi app

    event
        {
        "httpMethod": "GET",
        "headers": {},
        "url": "",
        "params": {},
        "multiValueParams": {},
        "pathParams": {},
        "multiValueHeaders": {},
        "queryStringParameters": {},
        "multiValueQueryStringParameters": {},
        "requestContext": {
                "identity": {"sourceIp": "95.170.134.34",
                             "userAgent": "Mozilla/5.0"},
                "httpMethod": "GET",
                "requestId": "0f61048c-2ba9",
                "requestTime": "18/Jun/2021:03:56:37 +0000",
                "requestTimeEpoch": 1623988597},
        "body": "",
        "isBase64Encoded": True
    }
    """
    with httpx.Client(app=app,
                      base_url=event['headers']['HTTP_HOST'], ) as client:
        request = client.build_request(
                method=event["httpMethod"],
                url=event["url"],
                headers=event["headers"],
                params=event["queryStringParameters"],
                content=json.dumps(event["body"]).encode(),
                )
        response = client.send(request)
        return response


def handler(event, context):
    config = load_config(CONFIG_FILENAME)
    app = load_app(config.get("entrypoint"),
                   config.get("django_settings_module"))
    response = call_app(app, event)
    return patch_response(response)
