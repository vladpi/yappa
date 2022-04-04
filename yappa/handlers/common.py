import logging
import os
import re
from base64 import b64decode

import httpx
import yaml

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

logger = logging.getLogger(__name__)
TOKEN_URL = ('http://169.254.169.254/computeMetadata/v1/'
             'instance/service-accounts/default/token')


def set_access_token(iam_token=None):
    if not iam_token:
        iam_token = ""
        try:
            resp = httpx.get(TOKEN_URL, headers={'Metadata-Flavor': 'Google'})
            if resp.status_code == 200:
                iam_token = resp.json()["access_token"]
        except (httpx.ConnectError, httpx.ConnectTimeout) as e:
            logger.error("couldn't fetch IAM token: %s", e)
    os.environ["IAM_TOKEN"] = iam_token


def load_yaml(file, safe=False):
    try:
        with open(file, "r") as f:
            return yaml.load(f.read(), Loader)
    except FileNotFoundError:
        if safe:
            return dict()
        else:
            raise


def body_to_bytes(event):
    if not event["body"]:
        pass
    elif event["isBase64Encoded"]:
        event["body"] = b64decode(event["body"])
    else:
        event["body"] = event["body"].encode()


DEFAULT_CONFIG_FILENAME = "yappa.yaml"

ENCODED_CONTENT_TYPES = (
    re.compile(r"image/.*"),
    re.compile(r"video/.*"),
    re.compile(r"audio/.*"),
    re.compile(r".*zip"),
    re.compile(r".*pdf"),
)


def get_encoding(response):
    content_type = response.headers["content-type"]
    for re_ in ENCODED_CONTENT_TYPES:
        if re_.match(content_type):
            return True


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
        'isBase64Encoded': get_encoding(response),
    }
