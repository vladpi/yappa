import os
from itertools import chain
from pathlib import Path
from uuid import uuid4

import pytest

from yappa.s3 import delete_bucket, ensure_bucket, get_s3_resource, \
    prepare_package, upload_to_bucket
from yappa.settings import DEFAULT_PACKAGE_DIR, DEFAULT_PROFILE_NAME

PROJECT_FILES = (
    Path("yappa.yaml"),
    Path("wsgi.py"),
    Path("package", "utils.py"),
    Path("package", "subpackage", "subutils.py")
)
IGNORED_FILES = (
    Path("requirements.txt"),
    Path(".idea"),
    Path(".git", "config"),
    Path("venv", "flask.py"),
)
IGNORED_PATTERNS = (
    ".idea",
    ".git",
    "venv",
    "requirements.txt",
)
PACKAGES = (
    "Flask",
    "yaml",
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
    prepare_package(REQUIREMENTS_FILE, IGNORED_PATTERNS)
    for path in chain(PROJECT_FILES, PACKAGES):
        assert os.path.exists(Path(DEFAULT_PACKAGE_DIR, path)), path
    for path in IGNORED_FILES:
        assert not os.path.exists(Path(DEFAULT_PACKAGE_DIR, path)), os.listdir()


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


def test_s3_upload(project_dir, bucket_name, profile):
    dir = prepare_package(to_install_requirements=False)
    object_key = upload_to_bucket(dir, bucket_name, profile)
    assert bucket_name in get_bucket_names(profile)
    bucket = ensure_bucket(bucket_name, profile)
    keys = [o.key for o in bucket.objects.all()]
    assert object_key in keys, keys
    delete_bucket(bucket_name, profile)
    assert bucket_name not in get_bucket_names(profile)
