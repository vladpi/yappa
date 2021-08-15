from click import ClickException


def validate_requirements_file(requirements_filename):
    with open(requirements_filename) as f:
        requirements = f.read()
    if "yappa" not in requirements:
        raise ClickException("'yappa' package should be in requirements. "
                             "Please update requirements running "
                             "'$pip freeze > requirements.txt'")