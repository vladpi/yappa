import json
from urllib.parse import urljoin

import pytest

from yappa.handler import call_app, load_app, patch_response


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
SAMPLE_RESPONSE = "root url"
BASE_URL = "http://base-url.com"


@pytest.fixture(params=[
        "test_apps.flask_app.app",
        pytest.param("test_apps.django_app.app", marks=pytest.mark.skip),
        ])
def app(request):
    return load_app(request.param)


def test_app_load(app):
    assert app
    assert callable(app)


def test_sample_call(app, sample_event):
    response = patch_response(call_app(app, sample_event))
    assert response["statusCode"] == 200
    assert response["body"] == SAMPLE_RESPONSE


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

