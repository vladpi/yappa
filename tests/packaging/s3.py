import os
from pathlib import Path
from uuid import uuid4

import boto3
import pytest

from yappa.packaging.s3 import (
    delete_bucket, ensure_bucket,
    prepare_package, upload_to_bucket,
)
from yappa.settings import (
    DEFAULT_CONFIG_FILENAME, DEFAULT_PACKAGE_DIR,
    YANDEX_S3_URL,
)

IGNORED_FILES = (
    Path("flask_requirements.txt"),
    Path(".idea"),
    Path(".git", "config"),
    Path("venv", "flask.py"),
)


@pytest.fixture
def expected_paths(config):
    *entrypoint_dirs, entrypoint_file = config["entrypoint"].split(".")[:-1]
    return [
        DEFAULT_CONFIG_FILENAME,
        Path("handlers", "wsgi.py"),
        Path("package", "utils.py"),
        Path("package", "subpackage", "subutils.py"),
        Path(*entrypoint_dirs, f"{entrypoint_file}.py"),
    ]


def test_files_copy(app_dir, config, expected_paths, config_filename):
    prepare_package(config["requirements_file"], config["excluded_paths"],
                    to_install_requirements=False,
                    config_filename=config_filename)
    for path in expected_paths:
        assert os.path.exists(Path(DEFAULT_PACKAGE_DIR, path)), path
    for path in IGNORED_FILES:
        assert not os.path.exists(
            Path(DEFAULT_PACKAGE_DIR, path)), os.listdir()


@pytest.fixture
def bucket_name():
    return "testbucket-" + str(uuid4())[:8]


def get_bucket_names(aws_access_key_id, aws_secret_access_key):
    buckets = boto3.resource(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        endpoint_url=YANDEX_S3_URL,
    ).buckets.all()
    return [b.name for b in buckets]


def test_s3_credentials(s3_credentials):
    assert "aws_access_key_id" in s3_credentials
    assert "aws_secret_access_key" in s3_credentials


def test_bucket_creation(bucket_name, s3_credentials):
    assert bucket_name not in get_bucket_names(**s3_credentials)

    ensure_bucket(bucket_name, **s3_credentials)
    assert bucket_name in get_bucket_names(**s3_credentials)

    delete_bucket(bucket_name, **s3_credentials)
    assert bucket_name not in get_bucket_names(**s3_credentials)


def test_s3_upload(app_dir, bucket_name, s3_credentials, config,
                   config_filename):
    dir = prepare_package(to_install_requirements=False,
                          config_filename=config_filename,
                          requirements_file=config["requirements_file"])
    object_key = upload_to_bucket(dir, bucket_name, **s3_credentials)
    assert bucket_name in get_bucket_names(**s3_credentials)
    bucket = ensure_bucket(bucket_name, **s3_credentials)
    keys = [o.key for o in bucket.objects.all()]
    assert object_key in keys, keys
    delete_bucket(bucket_name, **s3_credentials)
    assert bucket_name not in get_bucket_names(**s3_credentials)
