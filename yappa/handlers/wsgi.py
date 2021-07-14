import json
import logging
import os
from importlib import import_module
from pathlib import Path

import httpx
import yaml

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
DEFAULT_CONFIG_FILENAME = "yappa.yaml"
logger = logging.getLogger(__name__)


# TODO after yappa in pip - maybe move load_yaml to config_generation and
#  DEFAULT_CONFIG_FILENAME to settings
def load_yaml(file, safe=False):
    try:
        with open(file, "r") as f:
            return yaml.load(f.read(), Loader)
    except FileNotFoundError:
        if safe:
            return dict()
        else:
            raise


def save_yaml(config, filename):
    with open(filename, "w+") as f:
        f.write(yaml.dump(config, sort_keys=False))
    return filename


def load_app(import_path):
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
    app = load_app(config.get("entrypoint") or "")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                          config.get("django_settings_module") or "")
except ValueError:
    # logger.warning("Looks like broken Yappa config is used")
    pass  # TODO uncomment warning when yappa in pip and it load_config is moved from this file


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
