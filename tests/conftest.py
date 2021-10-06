import os
from pathlib import Path
from shutil import copy2

import pytest

from yappa.cli_helpers import create_function_version
from yappa.config_generation import create_default_config
from yappa.packaging.s3 import delete_bucket
from yappa.utils import save_yaml
from yappa.yc import YC


@pytest.fixture(scope="session")
def yc():
    return YC.setup()


COPIED_FILES = (
    Path(Path(__file__).resolve().parent, "test_apps", "flask_app.py"),
    Path(Path(__file__).resolve().parent, "test_apps",
         "flask_requirements.txt"),
)
PACKAGE_FILES = (
    Path("package", "utils.py"),
    Path("package", "subpackage", "subutils.py"),
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
    create_empty_files(*PACKAGE_FILES)
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
        project_slug="test-function-session",
        requirements_file="flask_requirements.txt",
        entrypoint="flask_app.app",
        application_type="wsgi",
        bucket="test-bucket-231",
        excluded_paths=(
            ".idea",
            ".git",
            "venv",
        )
    )
    save_yaml(config, config_filename)
    return config


@pytest.fixture(scope="session")
def function(config, yc):
    function, _ = yc.create_function(config["project_slug"])
    yield function
    yc.delete_function(config["project_slug"])


@pytest.fixture(scope="session",
                params=["s3", "direct"], ids=["s3", "direct"], )
def function_version(request, yc, function, config, config_filename,
                     s3_credentials):
    yield create_function_version(yc, config, request.param, config_filename)
    delete_bucket(config["bucket"], **s3_credentials)


@pytest.fixture(scope="session")
def s3_credentials(yc):
    return yc.get_s3_key()


@pytest.fixture()
def sample_event():
    return {
        "httpMethod": "GET",
        "headers": {
            "HTTP_HOST": ""
        },
        "url": "http://sampleurl.ru/",
        "params": {},
        "multiValueParams": {},
        "pathParams": {},
        "multiValueHeaders": {},
        "queryStringParameters": {},
        "multiValueQueryStringParameters": {},
        "requestContext": {
            "identity": {"sourceIp": "95.170.134.34",
                         "userAgent": "Mozilla/5.0"},
            "httpMethod": "GET",
            "requestId": "0f61048c-2ba9",
            "requestTime": "18/Jun/2021:03:56:37 +0000",
            "requestTimeEpoch": 1623988597},
        "body": "",
        "isBase64Encoded": False}
