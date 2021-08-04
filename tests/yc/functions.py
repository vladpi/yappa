from collections import Iterable

import httpx

from yappa.utils import convert_size_to_bytes, get_yc_entrypoint


def test_get_functions(yc):
    functions = yc._get_functions()
    assert isinstance(functions, Iterable)


def test_function_creation(yc):
    function_name = "create-delete-test-function"
    function, _ = yc.create_function(function_name)
    assert function.name == function_name
    assert function in yc._get_functions()
    yc.delete_function(function_name)
    assert function not in yc._get_functions()


def test_function_access(yc, function):
    assert yc._is_function_public(function.id) == True
    yc.set_function_access(function.id, is_public=False)
    assert yc._is_function_public(function.id) == False
    yc.set_function_access(function.id, is_public=True)


def test_function_version_creation(yc, function, function_version, config):
    version = yc.get_latest_version(function.id)
    assert version.entrypoint == get_yc_entrypoint(config["application_type"],
                                                   config["entrypoint"])
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
