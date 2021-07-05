from pathlib import Path

import yaml

from yappa.handle_wsgi import DEFAULT_CONFIG_FILENAME, load_config
from yappa.settings import DEFAULT_GW_CONFIG_FILENAME


def save_yaml(config, filename):
    with open(filename, "w+") as f:
        f.write(yaml.dump(config))
    return filename


def create_default_config(filename=DEFAULT_CONFIG_FILENAME):
    default_config = load_config(Path(Path(__file__).resolve().parent,
                                      "yappa.yaml"))
    save_yaml(default_config, filename)
    return default_config


def create_default_gw_config(filename=DEFAULT_GW_CONFIG_FILENAME):
    default_config = load_config(Path(Path(__file__).resolve().parent,
                                      "yappa-gw.yaml"))
    save_yaml(default_config, filename)
    return default_config


def inject_function_id(gw_config, function_id, title="yappa gateway"):
    """
    accepts gw config as dict, finds where to put function_id, returns new dict
    """
    gw_config["info"].update(title=title)
    for path, methods in gw_config["paths"].items():
        for method, description in methods.items():
            yc_integration = description.get("x-yc-apigateway-integration")
            if yc_integration \
                    and yc_integration["type"] == "cloud_functions" \
                    and not yc_integration["function_id"]:
                yc_integration.update(function_id=function_id)
    return gw_config


MIN_MEMORY, MAX_MEMORY = 134217728, 2147483648

SIZE_SUFFIXES = {
    'kb': 1024,
    'mb': 1024 * 1024,
    'gb': 1024 * 1024 * 1024,
}


def convert_size_to_bytes(size_str):
    for suffix in SIZE_SUFFIXES:
        if size_str.lower().endswith(suffix):
            size = int(size_str[0:-len(suffix)]) * SIZE_SUFFIXES[suffix]
            if not MIN_MEMORY <= size <= MAX_MEMORY:
                raise ValueError("Sorry. Due to YandexCloud limits, function "
                                 "memory should be between 128mB and 2GB")
            return size
    raise ValueError("Oops. Couldn't parse memory limit. "
                     "It should be in format 128MB, 2GB")


HANDLERS = {
    "wsgi": "handle_wsgi.handle",
}


def get_yc_entrypoint(application_type):
    entrypoint = HANDLERS.get(application_type)
    if not entrypoint:
        raise ValueError(
            f"Sorry, supported app types are: {','.join(HANDLERS.keys())}."
        )
    return entrypoint
