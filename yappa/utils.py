import yaml

CONFIG_FILENAME = "yappa.yaml"
AVAILABLE_PYTHON_VERSIONS = (
        "python38",
        "python37",
        )


def load_config(filename=CONFIG_FILENAME):
    with open(filename, "r") as f:
        return yaml.load(f.read())
