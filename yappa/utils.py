from pathlib import Path

import yaml

from yappa.settings import DEFAULT_CONFIG_FILENAME


def load_config(file=DEFAULT_CONFIG_FILENAME):
    """
    TODO is type checking necessary?
    """
    if isinstance(file, str) or isinstance(file, Path):
        with open(file, "r") as f:
            return yaml.load(f.read())
    return yaml.load(file.read())


def save_config(config, filename):
    with open(filename, "w+") as f:
        f.write(yaml.dump(config))
    return filename


def create_default_config(filename=DEFAULT_CONFIG_FILENAME):
    default_config = load_config(Path(Path(__file__).resolve().parent,
                                      "yappa.yaml"))
    save_config(default_config, filename)
    return default_config


MIN_MEMORY, MAX_MEMORY = 134217728, 2147483648

SIZE_SUFFIXES = {
    'kb': 1024,
    'mb': 1024 * 1024,
    'gb': 1024 * 1024 * 1024,
}


def convert_size_to_bytes(size_str):
    for suffix in SIZE_SUFFIXES:
        if size_str.lower().endswith(suffix):
            size = int(size_str[0:-len(suffix)]) * SIZE_SUFFIXES[suffix]
            if not MIN_MEMORY <= size <= MAX_MEMORY:
                raise ValueError("Sorry. Due to YandexCloud limits, function "
                                 "memory should be between 128mB and 2GB")
            return size
    raise ValueError("Oops. Couldn't parse memory limit. "
                     "It should be in format 128MB, 2GB")
