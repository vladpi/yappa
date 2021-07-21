from pathlib import Path

import pytest

from yappa.config_generation import inject_function_id
from yappa.utils import get_yc_entrypoint, load_yaml


@pytest.mark.parametrize(
        "application_type,expected_entrypoint,initial_entrypoint, is_ok", [
                ("wsgi", "handlers.wsgi.handle", "initial.entry_point", True),
                ("asgi", "handlers.asgi.handle", "initial.entry_point", True),
                ("raw", "initial.entry_point", "initial.entry_point", True),
                ("jibber_jabber", "flask", "initial_entrypoint", False),
                ])
def test_getting_entrypoint(application_type, expected_entrypoint,
                            initial_entrypoint, is_ok):
    if is_ok:
        entrypoint = get_yc_entrypoint(application_type, initial_entrypoint)
        assert entrypoint == expected_entrypoint
    else:
        with pytest.raises(ValueError):
            get_yc_entrypoint(application_type, expected_entrypoint)


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
    default_config = load_yaml(input)
    injected = inject_function_id(default_config, "test_function_id",
                                  "yappa_gateway")
    expected_config = load_yaml(expected_output)
    assert injected == expected_config
