from pathlib import Path

import pytest

from yappa.handle_wsgi import load_config
from yappa.utils import convert_size_to_bytes, get_yc_entrypoint, \
    inject_function_id


@pytest.mark.parametrize("input_str, expected_bytes, is_ok", [
    ("128mb", 134217728, True),
    ("512mb", 536870912, True),
    ("2GB", 2147483648, True),
    ("120mb", None, False),
    ("120kb", None, False),
    ("3GB", None, False),
    ("128x", None, False),
])
def test_size_conversion(input_str, expected_bytes, is_ok):
    if is_ok:
        assert convert_size_to_bytes(input_str) == expected_bytes
    else:
        with pytest.raises(ValueError):
            convert_size_to_bytes(input_str)


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
