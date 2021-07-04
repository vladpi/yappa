import click

from yappa.config_generation import generate_config_file, \
    generate_gw_config_file
from yappa.s3 import cleanup, delete_bucket, prepare_package, upload_to_bucket
from yappa.settings import DEFAULT_GW_CONFIG_FILENAME
from yappa.handle_wsgi import DEFAULT_CONFIG_FILENAME, load_config
from yappa.yc_function import create_function, delete_function, get_function_id, \
    set_access, \
    show_logs, \
    show_status, update_function
from yappa.yc_gateway import create_gw, delete_gw, update_gw


class NaturalOrderGroup(click.Group):

    def list_commands(self, ctx):
        return self.commands.keys()


@click.group(cls=NaturalOrderGroup)
def cli():
    pass


@cli.command()
@click.argument('config', type=click.Path(), default=DEFAULT_CONFIG_FILENAME)
@click.argument('gw_config', type=click.Path(),
                default=DEFAULT_GW_CONFIG_FILENAME)
def init(config_filename, gw_config_filename):
    """
    generation of configs & creation of function and api-gw

    if files with configs exist, then if just updates it
    \b
    - generates yappa.yaml
    - creates function
    - generates yappa-gw.yaml
    - creates api-gateway
    """
    generate_config_file(config_filename)
    config = load_config(config_filename)
    create_function()
    set_access(config["project_name"])

    function_id = get_function_id(config["project_name"])
    generate_gw_config_file(gw_config_filename, function_id)
    create_gw(gw_config_filename)


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


# TODO
if __name__ == '__main__':
    cli()
