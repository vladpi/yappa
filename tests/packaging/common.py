import pytest
from click import ClickException

from yappa.packaging.common import validate_requirements_file


@pytest.mark.parametrize("requirements,is_ok", [
    ("""
    sqlparse==0.4.1
    urllib3==1.26.6
    yandexcloud==0.98.0
    yappa==0.4.9
    """, True),
    ("""
    sqlparse==0.4.1
    urllib3==1.26.6
    yandexcloud==0.98.0
    """, False),
])
def test_requirements_validation(requirements, is_ok, tmpdir):
    filename = "tmp_requirements.txt"
    tmp_file = tmpdir.join(filename)
    tmp_file.write(requirements)
    if is_ok:
        validate_requirements_file(tmp_file)
    else:
        with pytest.raises(ClickException):
            validate_requirements_file(tmp_file)
