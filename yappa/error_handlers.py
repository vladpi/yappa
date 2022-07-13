import functools

import click
from grpc import RpcError


def handle_error(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RpcError as e:
            click.echo(f"{e.details()}")
            return
        except OSError as e:
            click.echo(f"{e}")
            return
    return wrapper
