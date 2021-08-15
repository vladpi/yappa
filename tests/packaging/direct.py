import os
from pathlib import Path

import pytest

from yappa.packaging.direct import (
    prepare_package, )
from yappa.settings import (
    DEFAULT_CONFIG_FILENAME, DEFAULT_PACKAGE_DIR,
)

IGNORED_FILES = (
    Path(".idea"),
    Path(".git", "config"),
    Path("venv", "flask.py"),
)


@pytest.fixture
def expected_paths(config):
    *entrypoint_dirs, entrypoint_file = config["entrypoint"].split(".")[:-1]
    return [
        "requirements.txt",
        DEFAULT_CONFIG_FILENAME,
        Path("handlers", "wsgi.py"),
        Path("package", "utils.py"),
        Path("package", "subpackage", "subutils.py"),
        Path(*entrypoint_dirs, f"{entrypoint_file}.py"),
    ]


def test_files_copy(app_dir, config, expected_paths, config_filename):
    prepare_package(config["requirements_file"], config["excluded_paths"],
                    config_filename=config_filename)
    for path in expected_paths:
        assert os.path.exists(Path(DEFAULT_PACKAGE_DIR, path)), path
    for path in IGNORED_FILES:
        assert not os.path.exists(
            Path(DEFAULT_PACKAGE_DIR, path)), os.listdir()
