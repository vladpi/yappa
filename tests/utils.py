import pytest

from yappa.settings import YANDEX_OAUTH_URL
from yappa.utils import convert_size_to_bytes


@pytest.mark.parametrize("input_str, expected_bytes, is_ok", [
        ("128mb", 134217728, True),
        ("512mb", 536870912, True),
        ("2GB", 2147483648, True),
        ("120mb", None, False),
        ("120kb", None, False),
        ("3GB", None, False),
        ("128x", None, False),
        ])
def test_size_conversion(input_str, expected_bytes, is_ok):
    if is_ok:
        assert convert_size_to_bytes(input_str) == expected_bytes
    else:
        with pytest.raises(ValueError):
            convert_size_to_bytes(input_str)


def test_oauth_url():
    assert YANDEX_OAUTH_URL == ("https://oauth.yandex.ru/authorize?"
                                "response_type=token"
                                "&client_id=9878e3bd8f1e4bc292ee9c74bbc736a2")
