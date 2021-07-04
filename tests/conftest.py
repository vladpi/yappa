import os
from pathlib import Path
from shutil import copy2

import pytest

from yappa.s3 import delete_bucket, prepare_package, \
    upload_to_bucket
from yappa.utils import create_default_config, \
    save_config
from yappa.yc import YC, load_credentials


@pytest.fixture(scope="session")
def yc():
    return YC(**load_credentials())


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
    for file in APP_FILES:
        copy2(file, ".")
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
def uploaded_package(config, app_dir):
    package_dir = prepare_package(config["requirements_file"],
                                  config["excluded_paths"],
                                  to_install_requirements=True,
                                  )
    object_key = upload_to_bucket(package_dir, config["bucket"],
                                  config["profile"])
    yield object_key
    delete_bucket(config["bucket"], config["profile"])


@pytest.fixture(scope="session")
def function_name():
    return "test-function-session"


@pytest.fixture(scope="session")
def function(function_name, yc):
    # TODO починить тесты если функция уже есть
    function = yc.create_function(function_name)
    yield function
    yc.delete_function(function.id)


@pytest.fixture(scope="session")
def function_version(yc, function, uploaded_package, config):
    return yc.create_function_version(
        function.id,
        runtime=config["runtime"],
        description=config["description"],
        entrypoint=config["entrypoint"],
        bucket_name=config["bucket"],
        object_name=uploaded_package,
        memory=config["memory_limit"],
        timeout=config["timeout"],
        environment=config["environment"],
        service_account_id=config["service_account_id"],
        named_service_accounts=config["named_service_accounts"],
    )
