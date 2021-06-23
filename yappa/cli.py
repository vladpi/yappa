import click

from yappa.s3 import delete_bucket, package, upload
from yappa.utils import load_config
from yappa.yc_function import (
    create_function, delete_function, show_logs,
    show_status,
    )
from yappa.yc_gateway import create_gw, delete_gw


@click.group()
def cli():
    pass


@cli.command(name='init')
def init_cmd():
    """
    generates config files
    - yappa.yaml
    - yappa-gw.yaml
    """
    pass


@cli.command(name='package')
@click.option('--file')
def package_cmd(file):
    config = load_config(file)
    package(**config)


@cli.command(name='upload')
@click.option('folder')
@click.option('bucket')
def upload_cmd(folder, bucket):
    upload(folder, bucket)


@cli.command(name='deploy')
@click.option('--file')
@click.option('--skip-requirements')
def deploy_cmd(file):
    config = load_config(file)
    create_function(**config)
    create_gw(**config)
    package(**config)
    upload(**config)


@cli.command(name='status')
@click.option('--file')
def status_cmd(file):
    config = load_config(file)
    show_status(config["function_name"])


@cli.command(name='logs')
@click.option('--file')
@click.option('--since')
@click.option('--until')
def logs_cmd(file, since, until):
    config = load_config(file)
    show_logs(config["function_name"], since, until)


@cli.command(name='delete')
@click.option('--file')
def delete_cmd(file):
    config = load_config(file)

    delete_function(**config)
    delete_gw(**config)
    delete_bucket(**config)


if __name__ == '__main__':
    cli()
