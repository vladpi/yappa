import os

import httpx

TOKEN_URL = 'http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token'


def set_access_token(iam_token=None):
    if not iam_token:
        resp = httpx.get(TOKEN_URL, headers={'Metadata-Flavor': 'Google'})
        iam_token = resp.json()["access_token"]
    os.environ["IAM_TOKEN"] = iam_token


def update_django_pg_connection(iam_token):
    from django.db import connections
    connections.databases["default"]["PASSWORD"] = iam_token
    # TODO not hard code db name
