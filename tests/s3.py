import os
from pathlib import Path
from uuid import uuid4

import pytest

from tests.conftest import (
    EMPTY_FILES, IGNORED_FILES,
    )
from yappa.s3 import (
    delete_bucket, ensure_bucket, get_s3_resource,
    prepare_package, upload_to_bucket,
    )
from yappa.settings import DEFAULT_PACKAGE_DIR, DEFAULT_PROFILE_NAME


@pytest.fixture
def expected_paths(config):
    *entrypoint_dirs, entrypoint_file = config["entrypoint"].split(".")[:-1]
    return [
            "handle_wsgi.py",
            *EMPTY_FILES,
            Path(*entrypoint_dirs, f"{entrypoint_file}.py"),
            ]


def test_files_copy(app_dir, config, expected_paths):
    prepare_package(config["requirements_file"], config["excluded_paths"],
                    to_install_requirements=False)
    for path in expected_paths:
        assert os.path.exists(Path(DEFAULT_PACKAGE_DIR, path)), path
    for path in IGNORED_FILES:
        assert not os.path.exists(
                Path(DEFAULT_PACKAGE_DIR, path)), os.listdir()


@pytest.fixture
def profile():
    return DEFAULT_PROFILE_NAME


@pytest.fixture
def bucket_name():
    return "testbucket-" + str(uuid4())[:8]


def get_bucket_names(profile):
    s3 = get_s3_resource(profile)
    bucket_names = [b.name for b in s3.buckets.all()]
    return bucket_names


def test_bucket_creation(bucket_name, profile):
    assert bucket_name not in get_bucket_names(profile)

    ensure_bucket(bucket_name, profile)
    assert bucket_name in get_bucket_names(profile)

    delete_bucket(bucket_name, profile)
    assert bucket_name not in get_bucket_names(profile)


def test_s3_upload(app_dir, bucket_name, profile):
    dir = prepare_package(to_install_requirements=False)
    object_key = upload_to_bucket(dir, bucket_name, profile)
    assert bucket_name in get_bucket_names(profile)
    bucket = ensure_bucket(bucket_name, profile)
    keys = [o.key for o in bucket.objects.all()]
    assert object_key in keys, keys
    delete_bucket(bucket_name, profile)
    assert bucket_name not in get_bucket_names(profile)
