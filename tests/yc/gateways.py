import os
from collections import Iterable

import httpx
import pytest
import yaml

from yappa.config_generation import create_default_gw_config, inject_function_id

if os.environ.get("SKIP_GATEWAY_TESTS"):
    pytest.skip("skipping gateway tests", allow_module_level=True)


@pytest.fixture(scope="session")
def gateway_name():
    return "test-gateway-231"


@pytest.fixture(scope="session")
def gateway_yaml(config, function, gateway_name):
    """
    reads default gw config and adds function_id
    """
    default_gw_config = create_default_gw_config()
    gw_config = inject_function_id(default_gw_config, function.id, gateway_name)
    return yaml.dump(gw_config)


@pytest.fixture(scope="session")
def gateway(gateway_yaml, yc, gateway_name):
    gw, _ = yc.create_gateway(gateway_name, gateway_yaml)
    yield gw
    yc.delete_gateway(gw.id)


def test_get_gateways(yc):
    gws = yc._get_gateways()
    assert isinstance(gws, Iterable)


def test_gateway_creation(gateway_yaml, yc):
    gateway_name = "test-create-delete-gateway"
    gateway, _ = yc.create_gateway(gateway_name, gateway_yaml)
    assert gateway in yc._get_gateways()
    yc.delete_gateway(gateway.id)
    assert gateway not in yc._get_gateways()


@pytest.mark.skip(reason="not yet implemented")
def test_gateway_update(gateway, yc):
    """
    1) change description and version
    2) change to dummy
    3) revert back
    """


def test_gateway_call(gateway, function_version):
    url = gateway.domain
    response = httpx.get(url)
    assert response.status_code == 200
    assert response.text == "root url"

    response = httpx.get(f"{url}/json")  # TODO compose url properly with furl
    assert response.status_code == 200
    assert response.json() == {"result": "json",
                               "sub_result": {"sub": "json"}
                               }
    num = "param"  # TODO generate random string or number?
    response = httpx.get(f"{url}/url_param/{num}")  # TODO compose url properly
    assert response.status_code == 200
    assert response.json() == {"param": num}

    # TODO add another two urls
