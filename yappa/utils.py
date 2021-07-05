from pathlib import Path
from uuid import uuid4

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


def is_valid_bucket_name(
        name):  # TODO change return False to raise ValidationError
    """
    Checks if an S3 bucket name is valid according to
    https://docs.aws.amazon.com/AmazonS3/latest/dev/BucketRestrictions.html#bucketnamingrules
    """
    # Bucket names must be at least 3 and no more than 63 characters long.
    if len(name) < 3 or len(name) > 63:
        return False
    # Bucket names must not contain uppercase characters or underscores.
    if any(x.isupper() for x in name):
        return False
    if "_" in name:
        return False
    # Bucket names must start with a lowercase letter or number.
    if not (name[0].islower() or name[0].isdigit()):
        return False
    # Bucket names must be a series of one or more labels.
    # Adjacent labels are separated by a single period (.).
    for label in name.split("."):
        # Each label must start and end with a lowercase letter or a number.
        if len(label) < 1:
            return False
        if not (label[0].islower() or label[0].isdigit()):
            return False
        if not (label[-1].islower() or label[-1].isdigit()):
            return False
    # Bucket names must not be formatted as an IP address
    # (for example, 192.168.5.4).
    looks_like_IP = True
    for label in name.split("."):
        if not label.isdigit():
            looks_like_IP = False
            break
    if looks_like_IP:
        return False

    return True


def is_valid_entrypoint():
    """
    try to import entrypoint. if is callable, then ok
    """


def is_valid_django_settings_module():
    """
    try to setup django app
    """


def is_valid_requirements_file():
    """
    try to open requirements. if it matches to re
    """


CONFIG = (
    ("project_name", "Yappa Project", [], "#TODO question"),
    ("description", "[empty]", [], "#TODO question"),
    ("entrypoint", "wsgi.app", [is_valid_entrypoint], "#TODO question"),
    ("django_settings_module", None, [is_valid_django_settings_module],
     "#TODO question"),
    ("bucket", "yappa-" + str(uuid4())[:8], [], "#TODO question"),
    ("requirements_file", "requirements.txt", [is_valid_requirements_file],
     "#TODO question")
)


def get_s3_profile():
    raise NotImplementedError


def get_missing_details(config):
    """
    if value is missing in config

    for values given in CONFIG ask for inputs, validate them
    find s3 profile
    """
    config["profile"] = get_s3_profile()
    return config
