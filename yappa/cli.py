import click


@click.group()
def cli():
    pass


@cli.command(name='init')
def init_cmd():
    pass


@cli.command(name='package')
@click.option('--file')
def package_cmd():
    pass


@cli.command(name='deploy')
@click.option('--file')
@click.option('--skip-requirements')
def deploy_cmd():
    pass


@cli.command(name='status')
@click.option('--file')
def status_cmd():
    pass


@cli.command(name='logs')
@click.option('--file')
@click.option('--since')
@click.option('--until')
def logs_cmd(since, until):
    pass


@cli.command(name='delete')
@click.option('--file')
def delete_cmd():
    pass


if __name__ == '__main__':
    cli()
