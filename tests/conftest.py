import os
from pathlib import Path
from shutil import copy2

import pytest

from yappa.config_generation import create_default_config
from yappa.handlers.wsgi import save_yaml
from yappa.s3 import delete_bucket, prepare_package, upload_to_bucket
from yappa.utils import get_yc_entrypoint
from yappa.yc import YC


@pytest.fixture(scope="session")
def yc():
    return YC.setup()


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


@pytest.fixture(scope="session")
def config_filename():
    return "yappa-config.yaml"


@pytest.fixture(scope="session")
def config(app_dir, config_filename):
    config = create_default_config(config_filename)
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
    save_yaml(config, config_filename)
    return config


@pytest.fixture(scope="session")
def uploaded_package(config, app_dir, s3_credentials, config_filename):
    package_dir = prepare_package(config["requirements_file"],
                                  config["excluded_paths"],
                                  to_install_requirements=True,
                                  config_filename=config_filename,
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
    function, _ = yc.create_function(function_name)
    yield function
    yc.delete_function(function.id)


@pytest.fixture(scope="session")
def function_version(yc, function, uploaded_package, config):
    return yc.create_function_version(
        function.name,
        runtime=config["runtime"],
        description=config["description"],
        entrypoint=get_yc_entrypoint(config["application_type"]),
        bucket_name=config["bucket"],
        object_name=uploaded_package,
        memory=config["memory_limit"],
        timeout=config["timeout"],
        environment=config["environment"],
        service_account_id=config["service_account_id"],
        named_service_accounts=config["named_service_accounts"],
    )


@pytest.fixture(scope="session")
def s3_credentials(yc):
    return yc.get_s3_key()
