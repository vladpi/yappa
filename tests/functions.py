import os
from pathlib import Path
from shutil import copy2

import pytest

from yappa.s3 import delete_bucket, ensure_bucket, prepare_package, \
    upload_to_bucket
from yappa.utils import create_default_config, load_config, save_config

APP_FILES = (
    Path(Path(__file__).resolve().parent, "test_apps", "flask_app.py"),
    Path(Path(__file__).resolve().parent, "test_apps",
         "flask_requirements.txt"),
)
CONFIG_FILENAME = "yappa.yaml"


@pytest.fixture(scope="session")
def app_dir(tmpdir_factory):
    package_dir = tmpdir_factory.mktemp('package')
    os.chdir(package_dir)
    return package_dir


@pytest.fixture(scope="session")
def config(app_dir):
    config = create_default_config()
    config.update(
        profile="default",
        requirements_file="flask_requirements.txt",
        entrypoint="flask_app.app",
        bucket="test-bucket-231",
    )
    save_config(config, CONFIG_FILENAME)
    return config


@pytest.fixture(scope="session")
def app(tmpdir_factory, app_dir):
    for file in APP_FILES:
        copy2(file, ".")


@pytest.fixture(scope="session")
def uploaded_package(app, config, app_dir):
    package_dir = prepare_package(config["requirements_file"],
                                  config["excluded_paths"])
    object_key = upload_to_bucket(package_dir, config["bucket"],
                                  config["profile"])
    yield object_key
    delete_bucket(config["bucket"], config["profile"])


def test_uploaded_package(uploaded_package, config):
    """
    almost duplicated test from tests/s3.py just to make sure that flask
    app is uploaded
    # TODO refactor, заменить эту фикстуру на те что используеются в s3
    """
    assert "yappa.yaml" in os.listdir("yappa_package")
    bucket = ensure_bucket(config["bucket"], config["profile"])
    keys = [o.key for o in bucket.objects.all()]
    assert uploaded_package in keys, keys


@pytest.fixture(scope="session")
def function_name():
    return "test-function-session"


@pytest.fixture(scope="session")
def function(function_name, yc):
    function = yc.create_function(function_name)
    yield function
    yc.delete_function(function.id)


@pytest.fixture(scope="session")
def function_version(yc, function, uploaded_package, config):
    pass
    # yc.create_function_version(
    #
    # )


def test_function_list(yc):
    functions = yc.get_functions()
    assert isinstance(functions, dict)


def test_function_creation(yc, function_name):
    assert function_name not in yc.get_functions()
    function = yc.create_function(function_name)
    assert function.name == function_name
    assert function_name in yc.get_functions()
    yc.delete_function(function.id)
    assert function_name not in yc.get_functions()


def test_function_access(yc, function):
    assert yc.is_function_public(function.id) == True
    yc.set_access(function.id, is_public=False)
    assert yc.is_function_public(function.id) == False
    yc.set_access(function.id, is_public=True)


def test_function_version_creation(yc, function_version):
    config = load_config()
    assert True
