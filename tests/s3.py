import os
from itertools import chain
from pathlib import Path

import pytest

from yappa.s3 import prepare_package
from yappa.settings import DEFAULT_PACKAGE_DIR

PROJECT_FILES = (
    Path("yappa.yaml"),
    Path("requirements.txt"),
    Path("wsgi.py"),
    Path("package", "utils.py"),
    Path("package", "subpackage", "subutils.py")
)
IGNORED_FILES = (
    Path(".idea"),
    Path(".git", "config"),
    Path("venv", "flask.py"),
)
PACKAGES = (
    "Flask",
    "PyYAML",
)
ADDITIONAL_FILES = (
    Path("handler.py"),
)
REQUIREMENTS = """Flask==2.0.1\nPyYAML==5.4.1"""
REQUIREMENTS_FILE = "requirements.txt"


def create_empty_files(*paths):
    for path in paths:
        os.makedirs(path.parent, exist_ok=True)
        open(path, "w").close()


@pytest.fixture()
def project_dir(tmp_path):
    os.chdir(tmp_path)
    assert not os.listdir()
    create_empty_files(*PROJECT_FILES, *IGNORED_FILES)
    with open(REQUIREMENTS_FILE, "w") as f:
        f.write(REQUIREMENTS)


def test_project_setup(project_dir):
    for path in chain(PROJECT_FILES, IGNORED_FILES):
        assert os.path.exists(path)
    with open(REQUIREMENTS_FILE, "r") as f:
        assert "Flask" in f.read()


def test_files_copy(project_dir):
    prepare_package(REQUIREMENTS_FILE)
    for path in chain(PROJECT_FILES, PACKAGES):
        assert os.path.exists(Path(DEFAULT_PACKAGE_DIR, path))
    for path in IGNORED_FILES:
        assert not os.path.exists(Path(DEFAULT_PACKAGE_DIR, path))
