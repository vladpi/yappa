import logging
from unittest.mock import Mock

import click
import yaml

from yappa.handle_wsgi import DEFAULT_CONFIG_FILENAME, load_config
from yappa.utils import (
    create_default_config, create_default_gw_config,
    get_missing_details, inject_function_id, save_yaml,
    )
from yappa.yc import load_credentials

logger = logging.getLogger(__name__)


class NaturalOrderGroup(click.Group):

    def list_commands(self, ctx):
        return self.commands.keys()


@click.group(cls=NaturalOrderGroup)
@click.pass_context
def cli(ctx):
    YC = Mock  # TODO remove mock
    ctx.ensure_object(dict)
    ctx.obj["yc"] = YC(**load_credentials())


@cli.command()
@click.argument("token", default="")
def setup(token):
    """
    setup for cloud access:
      - cloud_id
      - folder_id
      - service_account for s3
    """
    if not token:
        pass  # TODO ask for token, prompt url for getting it
    # https://cloud.yandex.ru/docs/iam/api-ref/grpc/
    # ask for cloud
    # ask for folder
    # look for service account "yappa", if not - create it
    # write credentials to .yappa


@cli.command(
        short_help='generate of config files, create function & api-gateway')
@click.pass_context
@click.argument('config_filename', type=click.Path(),
                default=DEFAULT_CONFIG_FILENAME)
def init(ctx, config_filename):
    """
    generation of configs & creation of function and api-gw

    if files with configs exist, then if just deploys
    \b
    - generates yappa.yaml
    - creates function
    - generates yappa-gw.yaml
    - creates api-gateway
    """
    config = (load_config(config_filename, safe=True)
              or create_default_config(config_filename))
    config = get_missing_details(config)
    save_yaml(config, config_filename)
    click.echo("saved Yappa config file at "
               + click.style(config_filename, bold=True))
    yc = ctx.obj["yc"]
    click.echo("Creating function...")
    function = yc.create_function(config["project_name"])
    click.echo("Created serverless function:\n"
               "\tid: " + click.style(f"{function.id}") + "\n"
               + "\tdefault domain : " + click.style(f"{function.invoke_url}",
                                                     fg="yellow"))

    gw_config_filename = config["gw_config"]
    gw_config = (load_config(gw_config_filename, safe=True)
                 or create_default_gw_config(gw_config_filename))
    gw_config = inject_function_id(gw_config, f"test_id", config[
        "project_name"])  # TODO remove test id
    save_yaml(gw_config, gw_config_filename)
    click.echo("saved Yappa Gateway config file at "
               + click.style(gw_config_filename, bold=True))
    click.echo("Creating api-gateway...")
    gateway = yc.create_gateway(config["project_name"], yaml.dump(gw_config))
    click.echo("Created api-gateway:\n"
               "\tid: " + click.style(f"{gateway.id}", ) + "\n"
               + "\tdefault domain : " + click.style(f"{gateway.domain}",
                                                     fg="yellow"))


@cli.command(short_help="creates new function version and updates api-gateway")
@click.option('--file', type=click.File('rb'), default=DEFAULT_CONFIG_FILENAME,
              help="yappa settings file")
def update(file):
    """\b
    - prepares package
    - uploads package to s3
    - creates new function version
    - updates api-gw
    """
    config = load_config(file)


@cli.command()
@click.option('--file', type=click.File('rb'), default=DEFAULT_CONFIG_FILENAME,
              help="yappa settings file")
def status(file):
    """
    display status of function and gateway
    """
    config = load_config(file)


@cli.command()
@click.option('--file', type=click.File('rb'), default=DEFAULT_CONFIG_FILENAME,
              help="yappa settings file")
def undeploy(file):
    """
    deletes function, api-gateway and bucket
    """
    config = load_config(file)


if __name__ == '__main__':
    cli(obj={})
