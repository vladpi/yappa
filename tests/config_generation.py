from pathlib import Path

import pytest

from yappa.config_generation import get_yc_entrypoint, inject_function_id
from yappa.handle_wsgi import load_config


@pytest.mark.parametrize("application_type,expected_entrypoint,is_ok", [
    ("wsgi", "handle_wsgi.handle", True),
    ("asgi", "handle_asgi.handle", False),
])
def test_getting_entrypoint(application_type, expected_entrypoint, is_ok):
    if is_ok:
        entrypoint = get_yc_entrypoint(application_type)
        assert entrypoint == expected_entrypoint
    else:
        with pytest.raises(ValueError):
            get_yc_entrypoint(application_type)


BASE_GW_DIR = Path(Path(__file__).resolve().parent, "gateway_configs")
SRC_GW_DIR = Path(BASE_GW_DIR, "src")
OUTPUT_GW_DIR = Path(BASE_GW_DIR, "output")


@pytest.mark.parametrize("input,expected_output", [
    (Path(SRC_GW_DIR, "yappa-gw-base.yaml"),
     Path(OUTPUT_GW_DIR, "yappa-gw-base.yaml")),
    (Path(SRC_GW_DIR, "yappa-gw-pwa.yaml"),
     Path(OUTPUT_GW_DIR, "yappa-gw-pwa.yaml")),
])
def test_gw_injection(input, expected_output):
    default_config = load_config(input)
    injected = inject_function_id(default_config, "test_function_id",
                                  "yappa_gateway")
    expected_config = load_config(expected_output)
    assert injected == expected_config
