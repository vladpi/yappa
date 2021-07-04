import httpx
import pytest


@pytest.mark.skip(reason="not yet implemented")
def test_gw_config_update(function, config):
    """
    test if correct yaml is produced
    """


@pytest.fixture(scope="session")
def gateway_name():
    return "test-gateway-231"


@pytest.fixture(scope="session")
def gateway_yaml(config):
    """
    reads default gw config and adds function_id
    """
    pass


@pytest.fixture(scope="session")
def gateway(gateway_yaml, yc):
    gw = yc.create_gateway()
    yield gw


@pytest.mark.skip(reason="not yet implemented")
def test_get_gateways(yc):
    gws = yc.get_gateways()
    assert isinstance(gws, dict)


@pytest.mark.skip(reason="not yet implemented")
def test_gateway_creation(gateway, gateway_name, yc):
    assert gateway_name in yc.get_gateways()


@pytest.mark.skip(reason="not yet implemented")
def test_gateway_update():
    pass


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
