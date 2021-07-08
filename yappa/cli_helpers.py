from uuid import uuid4

import click
from boltons.strutils import slugify
from click import ClickException

from yappa.cli import prepare_package, upload_to_bucket


class NaturalOrderGroup(click.Group):

    def list_commands(self, ctx):
        return self.commands.keys()


def create_function_version(config, yc):
    click.echo("Preparing package...")
    package_dir = prepare_package(config["requirements_file"],
                                  config["excluded_paths"],
                                  to_install_requirements=True,
                                  )
    click.echo(f"Uploading to bucket {config['bucket']}...")
    object_key = upload_to_bucket(package_dir, config["bucket"],
                                  **yc.get_s3_key(config["s3_account_name"]))
    function = yc.get_function(config["project_slug"])
    click.echo(f"Creating new function version for "
               + click.style(f"{function.name}", bold=True)
               + f" (id: {function.id})")
    yc.create_function_version(
        function.id,
        runtime=config["runtime"],
        description=config["description"],
        bucket_name=config["bucket"],
        object_name=object_key,
        application_type=config["application_type"],
        memory=config["memory_limit"],
        service_account_id=config["service_account_id"],
        timeout=config["timeout"],
        named_service_accounts=config["named_service_accounts"],
        environment=config["environment"],
    )
    click.echo(f"Created function version. Invoke url: "
               + click.style(f"{function.invoke_url}", fg="yellow"))


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