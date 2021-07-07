from pathlib import Path
from uuid import uuid4

import click
import yaml
from boltons.strutils import slugify
from click import ClickException

from yappa.handle_wsgi import DEFAULT_CONFIG_FILENAME, load_config
from yappa.settings import DEFAULT_GW_CONFIG_FILENAME


def save_yaml(config, filename):
    with open(filename, "w+") as f:
        f.write(yaml.dump(config, sort_keys=False))
    return filename


def create_default_config(filename=DEFAULT_CONFIG_FILENAME):
    default_config = load_config(Path(Path(__file__).resolve().parent,
                                      "yappa.yaml"))
    save_yaml(default_config, filename)
    return default_config


def create_default_gw_config(filename=DEFAULT_GW_CONFIG_FILENAME):
    default_config = load_config(Path(Path(__file__).resolve().parent,
                                      DEFAULT_GW_CONFIG_FILENAME))
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


class ValidationError(ClickException):
    pass


def is_valid_bucket_name(bucket_name):
    """
    Checks if an S3 bucket name is valid according to
    https://docs.aws.amazon.com/AmazonS3/latest/dev/BucketRestrictions.html
    """
    if len(bucket_name) < 3 or len(bucket_name) > 63:
        raise ValidationError("Bucket names must be at least 3 and no more "
                              "than 63 characters long.")
    if bucket_name.lower() != bucket_name or "_" in bucket_name:
        raise ValidationError("Bucket names must not contain uppercase"
                              " characters or underscores")
    for label in bucket_name.split("."):
        if len(label) < 1 \
                or not (label[0].islower() or label[0].isdigit()) \
                or not (label[-1].islower() or label[-1].isdigit()):
            raise ValidationError("Each label must start and end with a "
                                  "lowercase letter or a number")
    if all([s.isdigit() for s in bucket_name.split(".")]):
        raise ValidationError("Bucket names must not be formatted as an "
                              "IP address (i.e. 192.168.5.4)")


def is_valid_entrypoint(entrypoint):
    """
    try to import entrypoint. if is callable, then ok
    """


def is_valid_django_settings_module(django_settings_module):
    """
    try to setup django app
    """


def is_valid_requirements_file(requirements_file):
    """
    try to open requirements. if it matches to re
    """


def get_bucket_name(config):
    """
    generates bucket name, i.e. Yappa Project -> yappa.bucket-32139
    """
    return config['project_slug'].replace("_", ".") + f"-{str(uuid4())[:8]}"


def is_not_empty(string):
    if not string or not string.strip():
        raise ValidationError("should not be empty")


def get_slug(config):
    return slugify(config["project_name"])


PROMPTS = (
        ("project_name", "My project", [is_not_empty],
         "What's your project name?"),
        ("project_slug", get_slug, [],
         "What's your project slug?"),
        ("description", "", [],
         "What's your project description?"),
        ("entrypoint", "wsgi.app", [is_valid_entrypoint],
         "Please specify entrypoint (skip if it is Django project)"),
        ("django_settings_module", "", [is_valid_django_settings_module],
         "Please specify Django settings module"),
        ("bucket", get_bucket_name, [is_not_empty,
                                     is_valid_bucket_name],
         "Please specify bucket name"),
        ("requirements_file", "requirements.txt", [is_not_empty,
                                                   is_valid_requirements_file],
         "Please specify requirements file")
        )


def get_s3_profile():
    return "default"


def get_missing_details(config):
    """
    if value is missing in config prompt user
    """
    for key, default, validators, question in PROMPTS:
        if config.get(key) is not None:
            continue
        default = default(config) if callable(default) else default
        value = click.prompt(question, default=default)
        for validator in validators:
            validator(value)
        config[key] = value
    config["profile"] = get_s3_profile()
    return config
