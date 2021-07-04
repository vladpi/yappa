import pytest

from yappa.yc import YC, load_credentials


@pytest.fixture(scope="session")
def yc():
    return YC(**load_credentials())
