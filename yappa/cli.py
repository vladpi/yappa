import logging
from unittest.mock import Mock

import click
import yaml

from yappa.config_generation import (
    create_default_config, create_default_gw_config,
    get_missing_details, inject_function_id, save_yaml,
)
from yappa.handle_wsgi import DEFAULT_CONFIG_FILENAME, load_config
from yappa.s3 import prepare_package, upload_to_bucket
from yappa.yc import YC, load_credentials

logger = logging.getLogger(__name__)

YC = prepare_package = upload_to_bucket = Mock  # TODO remove mock


class NaturalOrderGroup(click.Group):

    def list_commands(self, ctx):
        return self.commands.keys()


@click.group(cls=NaturalOrderGroup)
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)
    ctx.obj["yc"] = YC(**load_credentials())


@cli.command(short_help="setup YC access")
@click.pass_context
@click.argument("token", default="")
def setup(token):
    """
    setup of cloud access:

    \b
      - cloud_id
      - folder_id
      - service_account for s3

    *you can skip this step if provide credentials in env vars (see README)
    """
    if not token:
        pass  # TODO ask for token, prompt url for getting it
    # ask for token
    # ask for folder, save it to config
    # create service account
    # generate .yc with credentials
    # save service_account_name to config


@cli.command(short_help='generate config files, create function & api-gateway')
@click.pass_context
@click.argument('config_filename', type=click.Path(),
                default=DEFAULT_CONFIG_FILENAME)
def init(ctx, config_filename):
    """\b
    - generates yappa.yaml (skipped if file exists)
    - creates function
    - generates yappa-gw.yaml (skipped if file exists)
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
    function = yc.create_function(config["project_slug"])
    click.echo("Created serverless function:\n"
               "\tname: " + click.style(f"{function.name}") + "\n"
                                                              "\tid: " +
               click.style(
                   f"{function.id}") + "\n"
               + "\tinvoke url : " + click.style(f"{function.invoke_url}",
                                                 fg="yellow"))

    gw_config_filename = config["gw_config"]
    gw_config = (load_config(gw_config_filename, safe=True)
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
@click.pass_context
@click.option('--file', type=click.File('rb'), default=DEFAULT_CONFIG_FILENAME,
              help="yappa settings file")
def deploy(ctx, file):
    """\b
    - prepares package
    - uploads package to s3
    - creates new function version
    - updates api-gw
    """
    config = load_config(file)
    yc = ctx.obj["yc"]
    click.echo("Preparing package...")
    package_dir = prepare_package(config["requirements_file"],
                                  config["excluded_paths"],
                                  to_install_requirements=True,
                                  )
    click.echo(f"Uploading to bucket {config['bucket']}...")
    object_key = upload_to_bucket(package_dir, config["bucket"],
                                  config["profile"])
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
    gateway = yc.get_gateway(config["project_slug"])
    click.echo(f"Updating api-gateway "
               + click.style(f"{gateway.name}", bold=True)
               + f" (id: {gateway.id})")
    yc.update_gateway(gateway.id, config["description"],
                      load_config(config["gw_config"]))
    click.echo(f"Updated api-gateway. Default domain: "
               + click.style(f"{function.invoke_url}", fg="yellow"))


@cli.command()
@click.option('--file', type=click.File('rb'), default=DEFAULT_CONFIG_FILENAME,
              help="yappa settings file")
def status(file):
    """
    display status of function and api-gateway
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
