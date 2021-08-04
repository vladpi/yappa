import json
import logging
import os
from importlib import import_module
from pathlib import Path

import httpx

from yappa.settings import DEFAULT_CONFIG_FILENAME
from yappa.utils import load_yaml
from .handle_utils import (set_access_token, update_django_pg_connection)

logger = logging.getLogger(__name__)


def load_app(import_path, django_settings_module=None):
    if not import_path:
        raise ValueError("import_path should not be empty")
    os.environ["DJANGO_SETTINGS_MODULE"] = django_settings_module or ""
    *submodules, app_name = import_path.split(".")
    module = import_module(".".join(submodules))
    app = getattr(module, app_name)
    return app


def call_app(app, event):
    """
    call wsgi app
    see https://cloud.yandex.ru/docs/functions/concepts/function-invoke
    #response
    """
    host_url = event["headers"].get("Host", "https://raw-function.net")
    if not host_url.startswith("http"):
        host_url = f"https://{host_url}"
    with httpx.Client(app=app,
                      base_url=host_url) as client:
        request = client.build_request(
            method=event["httpMethod"],
            url=event["url"],
            headers=event["headers"],
            params=event["queryStringParameters"],
            json=json.loads(event["body"]) if event["body"] else None,
        )
        response = client.send(request)
        return response


try:
    set_access_token()
    config = load_yaml(Path(Path(__file__).resolve().parent.parent,
                            DEFAULT_CONFIG_FILENAME))

    app = load_app(config.get("entrypoint"),
                   config.get("django_settings_module"))
except ValueError:
    logger.warning("Couldn't load app. Looks like broken Yappa config is used")


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


def handle(event, context):
    set_access_token()
    if not event:
        raise ValueError("Got empty event")

    if config["django_settings_module"]:
        update_django_pg_connection(context.token["access_token"])
        # TODO check if it's necessary to update db settings
    response = call_app(app, event)
    return patch_response(response)
