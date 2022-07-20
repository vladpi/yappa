# pylint: disable=redefined-outer-name
import json
import os
from collections.abc import Iterable

import pytest

from yappa.yc.access import save_key


def test_clouds(yc):
    clouds = yc.get_clouds()
    assert isinstance(clouds, Iterable)


@pytest.fixture
def cloud(yc):
    return yc.get_clouds()[0]


def test_folders(yc, cloud):
    folders = yc.get_folders(cloud.id)
    assert isinstance(folders, Iterable)


@pytest.fixture
def key(yc):
    account = yc.create_service_account("yappa-test-create-delete-account-2")
    key = yc.create_service_account_key(account.id)
    yield key
    yc.delete_key(key["id"])


@pytest.fixture
def saved_key(key):
    filepath = save_key(key)
    yield filepath
    os.remove(filepath)


def test_key_saving(saved_key, key):
    with open(saved_key, "r", encoding="utf-8") as f:
        saved_key = json.loads(f.read())
    assert key == saved_key


def test_iam_token(yc):
    token = yc.get_iam_token()
    assert token
