from collections import Iterable

import httpx
import pytest
import yaml

from yappa.config_generation import create_default_gw_config, inject_function_id


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
    gw = yc.create_gateway(gateway_name, gateway_yaml)
    yield gw
    yc.delete_gateway(gw.id)


@pytest.mark.skip(reason="not yet implemented")
def test_get_gateways(yc):
    gws = yc.get_gateways()
    assert isinstance(gws, Iterable)


@pytest.mark.skip(reason="not yet implemented")
def test_gateway_creation(gateway, gateway_name, yc):
    assert gateway_name in yc.get_gateways()
    # TODO test gateway delete


@pytest.mark.skip(reason="not yet implemented")
def test_gateway_update(gateway, yc):
    """
    1) change description and version
    2) change to dummy
    3) revert back
    """


@pytest.mark.skip(reason="not yet implemented")
def test_gateway_call(gateway, function_version):
    url = gateway.domain
    response = httpx.get(url)
    assert response.status_code == 200
    assert response.text == "root url"

    response = httpx.get(f"{url}/json")  # TODO compose url properly
    assert response.status_code == 200
    assert response.json() == {"result": "json",
                               "sub_result": {"sub": "json"}
                               }
    num = "param"  # TODO generate random string or number?
    response = httpx.get(f"{url}/url_param/{num}")  # TODO compose url properly
    assert response.status_code == 200
    assert response.json() == {"param": num}

    # TODO add another two urls
