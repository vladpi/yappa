import logging
from unittest.mock import Mock

import click
import yaml

from yappa.cli_helpers import NaturalOrderGroup, create_function_version, \
    get_missing_details
from yappa.config_generation import (
    create_default_config, create_default_gw_config,
    inject_function_id, )
from yappa.handle_wsgi import DEFAULT_CONFIG_FILENAME, load_yaml, save_yaml

logger = logging.getLogger(__name__)

YC = prepare_package = upload_to_bucket = Mock  # TODO remove mock


@click.group(cls=NaturalOrderGroup)
def cli():
    pass


@cli.command(short_help="setup YC access")
@click.argument('config-file', type=click.File('rb'),
                default=DEFAULT_CONFIG_FILENAME, help="yappa settings file")
def setup(config_file):
    """
    setup of cloud access:

    \b
      - asks for OAuth token
      - asks for cloud to work with
      - asks for folder to work with
      - creates service account (editor) and saves access key to .yc
      - saves folder_id and s3_account_name to yappa.yaml


    *you can skip this step if YC_OAUTH and YC_FOLDER in env vars
    (see README for authentication details)
    """




@cli.command(short_help='generate config files, create function & api-gateway')
@click.argument('config-file', type=click.File('rb'),
                default=DEFAULT_CONFIG_FILENAME, help="yappa settings file")
def deploy(config_file):
    """\b
    - generates yappa.yaml (skipped if file exists)
    - creates function
    - creates function version (with uploaded to s3 package)
    - generates yappa-gw.yaml (skipped if file exists)
    - creates api-gateway
    """
    config = (load_yaml(config_file, safe=True)
              or create_default_config(config_file))
    config = get_missing_details(config)
    save_yaml(config, config_file)
    click.echo("saved Yappa config file at "
               + click.style(config_file, bold=True))
    yc = YC.setup(config)
    click.echo("Creating function...")
    function = yc.create_function(config["project_slug"])
    click.echo("Created serverless function:\n"
               "\tname: " + click.style(f"{function.name}") + "\n"
                                                              "\tid: " +
               click.style(
                   f"{function.id}") + "\n"
               + "\tinvoke url : " + click.style(f"{function.invoke_url}",
                                                 fg="yellow"))
    create_function_version(yc, config)

    gw_config_filename = config["gw_config"]
    gw_config = (load_yaml(gw_config_filename, safe=True)
                 or create_default_gw_config(gw_config_filename))
    gw_config = inject_function_id(gw_config, f"test_id", config[
        "project_slug"])  # TODO remove test id
    save_yaml(gw_config, gw_config_filename)
    click.echo("saved Yappa Gateway config file at "
               + click.style(gw_config_filename, bold=True))
    click.echo("Creating api-gateway...")
    gateway = yc.create_gateway(config["project_name"], yaml.dump(gw_config))
    click.echo("Created api-gateway:\n"
               "\tname: " + click.style(f"{gateway.name}") + "\n"
                                                             "\tid: " +
               click.style(
                   f"{gateway.id}", ) + "\n"
               + "\tdefault domain : " + click.style(f"{gateway.domain}",
                                                     fg="yellow"))


@cli.command(short_help="creates new function version and updates api-gateway")
@click.argument('config-file', type=click.File('rb'),
                default=DEFAULT_CONFIG_FILENAME, help="yappa settings file")
def update(config_file):
    """\b
    - prepares package
    - uploads package to s3
    - creates new function version
    - updates api-gw
    """
    config = load_yaml(config_file)
    yc = YC.setup(config)
    create_function_version(yc, config)
    gateway = yc.get_gateway(config["project_slug"])
    click.echo(f"Updating api-gateway "
               + click.style(f"{gateway.name}", bold=True)
               + f" (id: {gateway.id})")
    yc.update_gateway(gateway.id, config["description"],
                      load_yaml(config["gw_config"]))
    click.echo(f"Updated api-gateway. Default domain: "
               + click.style(f"{gateway.invoke_url}", fg="yellow"))


@cli.command()
@click.argument('config-file', type=click.File('rb'),
                default=DEFAULT_CONFIG_FILENAME, help="yappa settings file")
def undeploy(config_file):
    """
    deletes function, api-gateway and bucket
    """
    config = load_yaml(config_file)


if __name__ == '__main__':
    cli(obj={})
