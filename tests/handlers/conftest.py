import pytest


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