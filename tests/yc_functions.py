import os
from collections import Iterable

import httpx

from yappa.s3 import ensure_bucket
from yappa.config_generation import get_yc_entrypoint
from yappa.utils import convert_size_to_bytes


def test_uploaded_package(uploaded_package, config):
    """
    almost duplicated test from tests/s3.py just to make sure that flask
    app is uploaded
    # TODO refactor, заменить эту фикстуру на те что используеются в s3
    """
    assert "yappa.yaml" in os.listdir("yappa_package")
    bucket = ensure_bucket(config["bucket"], config["profile"])
    keys = [o.key for o in bucket.objects.all()]
    assert uploaded_package in keys, keys


def test_get_function(yc):
    functions = yc.get_functions()
    assert isinstance(functions, Iterable)


def test_function_creation(yc, function_name):
    assert function_name not in [f.name for f in yc.get_functions()]
    function = yc.create_function(function_name)
    assert function.name == function_name
    assert function in yc.get_functions()
    yc.delete_function(function.id)
    assert function not in yc.get_functions()
    # TODO refactor сделать тесты как у гейтвея.


def test_function_access(yc, function):
    assert yc.is_function_public(function.id) == True
    yc.set_function_access(function.id, is_public=False)
    assert yc.is_function_public(function.id) == False
    yc.set_function_access(function.id, is_public=True)


def test_function_version_creation(yc, function, function_version, config):
    version = yc.get_latest_version(function.id)
    assert version.entrypoint == get_yc_entrypoint(config["application_type"])
    assert version.resources.memory == convert_size_to_bytes(
            config["memory_limit"])
    assert version.execution_timeout.seconds == float(config["timeout"])
    if config["service_account_id"]:
        assert version.service_account_id == config["service_account_id"]
    else:
        assert not version.service_account_id
    assert version.environment == config["environment"]
    assert version.named_service_accounts == config["named_service_accounts"]


def test_function_call(function, function_version):
    url = function.http_invoke_url
    response = httpx.get(url)
    assert response.status_code == 200
    assert response.text == "root url"
