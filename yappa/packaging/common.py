import platform

from click import ClickException

REQUIRED_PACKAGES = ("httpx", "PyYAML")


def validate_requirements_file(requirements_filename):
    if any(platform.win32_ver()):
        return
    try:
        with open(requirements_filename, encoding="utf-8") as f:
            requirements = f.read()
    except FileNotFoundError:
        raise ClickException(
            "Couldn't find requirements file. Please specify "
            "it in yappa.yaml"
        )
    for package in REQUIRED_PACKAGES:
        if package not in requirements:
            raise ClickException(
                f"{package} package should be in requirements."
                "Please update requirements running "
                "'$pip freeze > requirements.txt'"
            )
