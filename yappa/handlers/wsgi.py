import json
import logging
import os
from importlib import import_module
from pathlib import Path

import httpx

from yappa.settings import DEFAULT_CONFIG_FILENAME
from yappa.utils import load_yaml


logger = logging.getLogger(__name__)


def load_app(import_path, django_settings_module=None):
    if not import_path:
        raise ValueError("import_path should not be empty")
    os.environ["DJANGO_SETTINGS_MODULE"] = django_settings_module or ""
    *submodules, app_name = import_path.split(".")
    module = import_module(".".join(submodules))
    app = getattr(module, app_name)
    return app


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
        'headers': dict(response.headers),
        'body': response.content.decode(),
        'isBase64Encoded': False,
    }


def call_app(app, event):
    """
    call wsgi app
    see https://cloud.yandex.ru/docs/functions/concepts/function-invoke
    #response
    """
    with httpx.Client(app=app,
                      base_url="http://host.url", ) as client:  # TODO where
        # do i find host url???
        request = client.build_request(
            method=event["httpMethod"],
            url=event["url"],
            headers=event["headers"],
            params=event["queryStringParameters"],
            content=json.dumps(event["body"]).encode(),
        )
        response = client.send(request)
        return response


try:
    config = load_yaml(Path(Path(__file__).resolve().parent.parent,
                            DEFAULT_CONFIG_FILENAME))

    app = load_app(config.get("entrypoint"),
                   config.get("DJANGO_SETTINGS_MODULE"))
except ValueError:
    logger.warning("Couldn't load app. Looks like broken Yappa config is used")
    pass


def handle(event, context):
    response = call_app(app, event)
    if not config["debug"]:
        return patch_response(response)
    return {
        'statusCode': 200,
        'body': {
            "event": event,
            "response": response,
        },
    }
