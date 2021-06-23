import click

from yappa.s3 import cleanup, delete_bucket, prepare_package, upload_to_bucket
from yappa.settings import DEFAULT_CONFIG_FILENAME, DEFAULT_GW_CONFIG_FILENAME
from yappa.utils import load_config
from yappa.yc_function import create_function, delete_function, set_access, \
    show_logs, \
    show_status, update_function
from yappa.yc_gateway import create_gw, delete_gw, prep_gw_config, update_gw


class NaturalOrderGroup(click.Group):

    def list_commands(self, ctx):
        return self.commands.keys()


@click.group(cls=NaturalOrderGroup)
def cli():
    pass


@cli.command()
@click.argument('config', type=click.Path(), default=DEFAULT_CONFIG_FILENAME)
@click.argument('gw_config', type=click.Path(), default=DEFAULT_GW_CONFIG_FILENAME)
def init(config, gw_config):
    """
    generation of configs & creation of function and api-gw

    if files with configs exist, then if just updates it
    \b
    - generates yappa.yaml
    - creates function
    - generates yappa-gw.yaml
    - creates api-gateway
    """
    # TODO add logic if files already exist. advanced scenario: existing configs
    name, description, memory, entrypoint = input
    version = '0.1'
    create_function(name, description)
    set_access(name)
    gw_config = prep_gw_config()
    create_gw(gw_config)


@cli.command()
@click.option('--file', type=click.File('rb'), default=DEFAULT_CONFIG_FILENAME,
              help="yappa settings file")
@click.option('--skip_requirements', is_flag=True,
              help="if to skip installing requirements to package folder")
def update(file):
    """\b
    - prepares package
    - uploads package to s3
    - updates function and api-gw version
    """
    config = load_config(file)
    prepare_package(**config)
    upload_to_bucket(**config)
    update_function()
    # make sure that update of bucket automatically updates function
    update_gw(**config)
    cleanup()


@cli.command()
@click.option('--file', type=click.File('rb'), default=DEFAULT_CONFIG_FILENAME,
              help="yappa settings file")
def status(file):
    """
    display status of function and gateway
    """
    config = load_config(file)
    show_status(config["function_name"])


@cli.command()
@click.option('--file', type=click.File('rb'), default=DEFAULT_CONFIG_FILENAME,
              help="yappa settings file")
@click.option('--since')
@click.option('--until')
def logs(file, since, until):
    """
    display logs of function
    """
    config = load_config(file)
    show_logs(config["function_name"], since, until)


@cli.command()
@click.option('--file', type=click.File('rb'), default=DEFAULT_CONFIG_FILENAME,
              help="yappa settings file")
def undeploy(file):
    """
    deletes function, api-gateway and bucket
    """
    # TODO add 'are you sure?'
    config = load_config(file)

    delete_function(**config)
    delete_gw(**config)
    delete_bucket(**config)


@cli.command()
@click.option('--file', type=click.File('rb'), default=DEFAULT_CONFIG_FILENAME,
              help="yappa settings file")
def package(file):
    """
    prepares package ready to be uploaded as serverless function
    """
    config = load_config(file)
    prepare_package(**config)


@cli.command()
@click.argument('folder', type=click.Path(exists=True))
@click.argument('bucket', type=click.STRING)
def upload(folder, bucket):
    """
    uploads given folder to s3 bucket
    """
    upload_to_bucket(folder, bucket)


if __name__ == '__main__':
    cli()
