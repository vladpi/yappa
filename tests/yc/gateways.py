from collections import Iterable

import httpx
import pytest
import yaml
from furl import furl

from yappa.config_generation import (
    create_default_gw_config,
    inject_function_id,
)


@pytest.fixture(scope="session")
def gateway_name():
    return "test-gateway-231"


@pytest.fixture(scope="session")
def gateway_yaml(config, function, gateway_name):
    """
    reads default gw config and adds function_id
    """
    default_gw_config = create_default_gw_config()
    gw_config = inject_function_id(default_gw_config, function.id,
                                   gateway_name)
    return yaml.dump(gw_config)


@pytest.fixture(scope="session")
def gateway(gateway_yaml, yc, gateway_name):
    gw, _ = yc.create_gateway(gateway_name, gateway_yaml)
    yield gw
    yc.delete_gateway(gateway_name)


def test_get_gateways(yc):
    gws = yc._get_gateways()
    assert isinstance(gws, Iterable)


def test_gateway_creation(gateway_yaml, yc):
    gateway_name = "test-create-delete-gateway"
    gateway, _ = yc.create_gateway(gateway_name, gateway_yaml)
    assert gateway in yc._get_gateways()
    yc.delete_gateway(gateway_name)
    assert gateway not in yc._get_gateways()


@pytest.mark.skip(reason="not yet implemented")
def test_gateway_update(gateway, yc):
    """
    1) change description and version
    2) change to dummy
    3) revert back
    """


def test_gateway_call(gateway, function_version, faker):
    f = furl(f"https://{gateway.domain}")
    response = httpx.get(f.url, timeout=300)
    assert response.status_code == 200, response.content
    assert response.text == "root url"

    response = httpx.get((f / "json").url)
    assert response.status_code == 200, response.content
    assert response.json() == {"result": "json",
                               "sub_result": {"sub": "json"}
                               }
    param_value = f"{faker.pyint}"
    response = httpx.get((f / "url_param" / param_value).url)
    assert response.status_code == 200, response.content
    assert response.json() == {"param": param_value}

    response = httpx.post((f / "post").url, json={"sample": "request"})
    assert response.status_code == 200, response.content
    assert response.json() == {"request": {"sample": "request"}}, \
        response.json()
