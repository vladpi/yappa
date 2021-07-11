import json
from collections import Iterable

import pytest

from yappa.settings import DEFAULT_ACCESS_KEY_FILE
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
    account = yc.create_service_account()
    key = yc.create_service_account_key(account.id)
    yield key
    yc.delete_key(key["id"])


def test_key_saving(key):
    save_key(key)
    with open(DEFAULT_ACCESS_KEY_FILE, "r") as f:
        saved_key = json.loads(f.read())
    assert key == saved_key
