import yaml

from yappa.settings import DEFAULT_CONFIG_FILENAME


def load_config(file=DEFAULT_CONFIG_FILENAME):
    """
    TODO is type checking necessary?
    """
    if isinstance(file, str):
        with open(file, "r") as f:
            return yaml.load(f.read)
    return yaml.load(file.read())
