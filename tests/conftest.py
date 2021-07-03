import pytest

from yappa.yc import YC, load_credentials


@pytest.fixture
def yc():
    return YC(**load_credentials())
