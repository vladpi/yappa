import json
import sys
from copy import copy
from pathlib import Path
from urllib.parse import urljoin

import pytest

from yappa.handlers.asgi import call_app
from yappa.handlers.wsgi import load_app, patch_response

BASE_URL = "http://base-url.com"


@pytest.fixture(params=[
    ("fastapi_app.app", None),
], ids=[
    "fastAPI",
], )
def app(request):
    # TODO сделать зависимой от config, а config - параметризованная фикстура
    # чтобы тесты handler, s3, yc_functions вызывались для каждого приложения
    sys.path.append(
        str(Path(Path(__file__).resolve().parent.parent, "test_apps")))
    return load_app(*request.param)


def test_app_load(app):
    assert app
    assert callable(app)


@pytest.mark.asyncio
async def test_sample_call(app, sample_event):
    response = await call_app(app, sample_event)
    response = patch_response(response)
    assert response["statusCode"] == 200
    assert response["body"] == 'root url'
    assert isinstance(response["headers"], dict)
    assert not isinstance(response['body'], bytes)


@pytest.mark.asyncio
async def test_not_found_call(app, sample_event):
    sample_event["url"] = urljoin(BASE_URL, "not-found")
    response = await call_app(app, sample_event)
    response = patch_response(response)
    assert response["statusCode"] == 404


@pytest.mark.asyncio
async def test_json_response(app, sample_event):
    sample_event["url"] = urljoin(BASE_URL, "json")
    response = await call_app(app, sample_event)
    response = patch_response(response)
    assert response["statusCode"] == 200
    assert response["body"].replace("\n", "") == json.dumps(
        {"result": "json", "sub_result": {"sub": "json"}}).replace(" ", "")


@pytest.mark.asyncio
async def test_post(app, sample_event):
    body = {"test_str": "ok!",
            "test_num": 5}
    event = copy(sample_event)
    event.update(
        url=urljoin(BASE_URL, "post"),
        httpMethod="POST",
        headers={"Content-Type": "application/json"},
        body=json.dumps(body),
    )
    response = await call_app(app, event)
    response = patch_response(response)
    assert response["statusCode"] == 200, response
    assert json.loads(response["body"])["request"] == body
