import os
from pathlib import Path
from shutil import copy2

import pytest

from yappa.config_generation import create_default_config, save_yaml
from yappa.s3 import delete_bucket, prepare_package, upload_to_bucket
from yappa.yc import YC, load_credentials


@pytest.fixture(scope="session")
def yc():
    return YC(**load_credentials())


COPIED_FILES = (
    Path(Path(__file__).resolve().parent, "test_apps", "flask_app.py"),
    Path(Path(__file__).resolve().parent, "test_apps",
         "flask_requirements.txt"),
)
EMPTY_FILES = (
    Path("package", "utils.py"),
    Path("package", "subpackage", "subutils.py")
)

IGNORED_FILES = (
    Path("requirements.txt"),
    Path(".idea"),
    Path(".git", "config"),
    Path("venv", "flask.py"),
)


def create_empty_files(*paths):
    for path in paths:
        os.makedirs(path.parent, exist_ok=True)
        open(path, "w").close()


@pytest.fixture(scope="session")
def app_dir(tmpdir_factory):
    dir_ = tmpdir_factory.mktemp('package')
    os.chdir(dir_)
    assert not os.listdir()
    create_empty_files(*EMPTY_FILES, *IGNORED_FILES)
    for file in COPIED_FILES:
        copy2(file, ".")
    return dir_


CONFIG_FILENAME = "yappa.yaml"


@pytest.fixture(scope="session")
def config(app_dir):
    config = create_default_config()
    config.update(
        profile="default",
        requirements_file="flask_requirements.txt",
        entrypoint="flask_app.app",
        bucket="test-bucket-231",
        excluded_paths=(
            ".idea",
            ".git",
            "venv",
            "requirements.txt",
        )
    )
    save_yaml(config, CONFIG_FILENAME)
    return config


@pytest.fixture(scope="session")
def uploaded_package(config, app_dir, s3_credentials):
    package_dir = prepare_package(config["requirements_file"],
                                  config["excluded_paths"],
                                  to_install_requirements=True,
                                  )
    object_key = upload_to_bucket(package_dir, config["bucket"],
                                  **s3_credentials)
    yield object_key
    delete_bucket(config["bucket"], **s3_credentials)


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
        application_type=config["application_type"],
        bucket_name=config["bucket"],
        object_name=uploaded_package,
        memory=config["memory_limit"],
        timeout=config["timeout"],
        environment=config["environment"],
        service_account_id=config["service_account_id"],
        named_service_accounts=config["named_service_accounts"],
    )


@pytest.fixture(scope="session")
def account_id():
    return "ajeibih4hnqeacs7qu3l"


@pytest.fixture(scope="session")
def s3_credentials(yc, account_id):
    return yc.create_s3_key(account_id)
