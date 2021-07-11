import logging

import click

from yappa.cli_helpers import NaturalOrderGroup, create_function, \
    create_function_version, \
    create_gateway, get_missing_details, update_gateway
from yappa.config_generation import (
    create_default_config, )
from yappa.handlers.wsgi import DEFAULT_CONFIG_FILENAME, load_yaml, save_yaml
from yappa.settings import DEFAULT_ACCESS_KEY_FILE, YANDEX_OAUTH_URL
from yappa.yc import YC
from yappa.yc.access import save_key

logger = logging.getLogger(__name__)


@click.group(cls=NaturalOrderGroup)
def cli():
    pass


@cli.command(short_help="setup YC access")
@click.argument("config-file", type=click.Path(exists=False),
                default=DEFAULT_CONFIG_FILENAME, )
@click.option("-t", '--token', default="",
              help="yandex OAuth token", envvar="YC_OAUTH"
              )
def setup(config_file, token):
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
    click.echo("Welcome to " + click.style("Yappa", fg="yellow") + "!")
    if not token:
        click.echo(f"Please obtain OAuth token at "
                   + click.style(YANDEX_OAUTH_URL, fg="yellow"))
        token = click.prompt("Please enter OAuth token")
    yc = YC.setup(token=token, skip_folder=True)
    clouds = {c.name: c.id for c in yc.get_clouds()}
    cloud_name = click.prompt("Please select cloud", type=click.Choice(clouds),
                              default=next(iter(clouds)))
    folders = {f.name: f.id for f in yc.get_folders(clouds[cloud_name])}
    folder_name = click.prompt("Please select folder",
                               type=click.Choice(folders),
                               default=next(iter(folders)))
    click.echo("Creating service account...")
    yc.folder_id = folders[folder_name]
    account = yc.create_service_account()
    save_key(yc.create_service_account_key(account.id))
    click.echo("Saved service account credentials at " + click.style(
        DEFAULT_ACCESS_KEY_FILE, bold=True))

    config = (load_yaml(config_file, safe=True)
              or create_default_config(config_file))
    config["folder_id"] = folders[folder_name]
    save_yaml(config, config_file)
    click.echo("Saved Yappa config file at "
               + click.style(config_file, bold=True))


@cli.command(short_help='generate config files, create function & api-gateway')
@click.argument("config-file", type=click.Path(exists=False),
                default=DEFAULT_CONFIG_FILENAME, )
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
    config, is_updated = get_missing_details(config)
    if is_updated:
        save_yaml(config, config_file)
        click.echo("saved Yappa config file at "
                   + click.style(config_file, bold=True))
    yc = YC.setup(config=config)
    function = create_function(yc, config)
    create_function_version(yc, config)
    is_new = create_gateway(yc, config, function.id)
    if not is_new:
        update_gateway(yc, config)


@cli.command()
@click.argument("config-file", type=click.Path(exists=True),
                default=DEFAULT_CONFIG_FILENAME, )
def undeploy(config_file):
    """
    deletes function, api-gateway and bucket
    """
    config = load_yaml(config_file)


if __name__ == '__main__':
    cli(obj={})
