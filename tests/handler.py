import json
import sys
from pathlib import Path
from urllib.parse import urljoin

import pytest

from yappa.handle_wsgi import call_app, load_app, patch_response


@pytest.fixture()
def sample_event():
    return {
            "httpMethod": "GET",
            "headers": {
                    "HTTP_HOST": ""
                    },
            "url": "http://sampleurl.ru/",
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
            "isBase64Encoded": True}


SAMPLE_CONTEXT = None
BASE_URL = "http://base-url.com"


@pytest.fixture(params=[
        # TODO add names of apps
        ("flask_app.app", None),
        (None, "django_app"),
        ])
def app(request):
    # TODO сделать зависоимой от config, а config - параметризованная фикстура
    # чтобы тесты handler, s3, yc_functions вызывались для каждого приложения
    sys.path.append(str(Path(Path(__file__).resolve().parent, "test_apps")))
    return load_app(*request.param)


def test_load_from_config(config):
    sys.path.append(str(Path(Path(__file__).resolve().parent, "test_apps")))
    app = load_app(config.get("entrypoint"),
                   config.get("django_settings_module"))
    assert callable(app)


def test_app_load(app):
    assert app
    assert callable(app)


def test_sample_call(app, sample_event):
    response = patch_response(call_app(app, sample_event))
    assert response["statusCode"] == 200
    assert response["body"] == "root url"
    assert isinstance(response["headers"], dict)
    assert not isinstance(response['body'], bytes)


def test_not_found_call(app, sample_event):
    sample_event["url"] = urljoin(BASE_URL, "not-found")
    response = patch_response(call_app(app, sample_event))
    assert response["statusCode"] == 404


def test_json_response(app, sample_event):
    sample_event["url"] = urljoin(BASE_URL, "json")
    response = patch_response(call_app(app, sample_event))
    assert response["statusCode"] == 200
    assert response["body"].replace("\n", "") == json.dumps(
            {"result": "json", "sub_result": {"sub": "json"}}).replace(" ", "")


def test_query_params(app, sample_event):
    sample_event["url"] = urljoin(BASE_URL, "query_params")
    params = {
            "a": "a_value",
            "b": "1",
            }
    sample_event["queryStringParameters"] = params
    response = patch_response(call_app(app, sample_event))
    assert response["statusCode"] == 200, response["body"]
    assert response["body"].replace("\n", "").replace(" ", "") == json.dumps(
            {"params": params}).replace(" ", "")


def test_url_param(app, sample_event):
    param_value = "random_param"  # TODO randomize
    sample_event["url"] = urljoin(BASE_URL, f"/url_param/{param_value}")
    response = patch_response(call_app(app, sample_event))
    assert response["statusCode"] == 200
    assert response["body"].replace("\n", "") == json.dumps(
            {"param": param_value}).replace(" ", "")


@pytest.mark.skip()
def test_post(app, sample_event):
    body = {"test_str": "ok!",
            "test_num": 5}
    sample_event["url"] = urljoin(BASE_URL, "post")
    sample_event["httpMethod"] = "POST"
    sample_event["body"] = body
    response = patch_response(call_app(app, sample_event))
    assert response["statusCode"] == 200, response
    assert json.loads(response["body"]) == {"request": body}
