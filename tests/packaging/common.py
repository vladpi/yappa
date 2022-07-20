import pytest
from click import ClickException

from yappa.packaging.common import validate_requirements_file
from yappa.packaging.direct import clear_requirements


@pytest.mark.parametrize(
    "requirements,is_ok",
    [
        (
            """
    sqlparse==0.4.1
    urllib3==1.26.6
    yandexcloud==0.98.0
    httpx==0.18.2
    PyYAML==5.4.1
    """,
            True,
        ),
        (
            """
    sqlparse==0.4.1
    urllib3==1.26.6
    yandexcloud==0.98.0
    """,
            False,
        ),
    ],
)
def test_requirements_validation(requirements, is_ok, tmpdir):
    filename = "tmp_requirements.txt"
    tmp_file = tmpdir.join(filename)
    tmp_file.write(requirements)
    if is_ok:
        validate_requirements_file(tmp_file)
    else:
        with pytest.raises(ClickException):
            validate_requirements_file(tmp_file)


@pytest.mark.parametrize(
    "requirements,cleared_requirements",
    [
        (
            """sqlparse==0.4.1
urllib3==1.26.6
yandexcloud==0.98.0
httpx==0.18.2
yappa>=0.4.9""",
            """sqlparse==0.4.1
urllib3==1.26.6
yandexcloud==0.98.0
httpx==0.18.2
""",
        ),
        (
            """sqlparse==0.4.2
urllib3==1.26.6
yandexcloud==0.98.0""",
            """sqlparse==0.4.2
urllib3==1.26.6
yandexcloud==0.98.0""",
        ),
    ],
)
def test_requirements_clearance(requirements, cleared_requirements, tmpdir):
    filename = "tmp_requirements.txt"
    tmp_file = tmpdir.join(filename)
    tmp_file.write(requirements)
    clear_requirements(tmp_file)
    with open(tmp_file, "r", encoding="utf-8") as f:
        assert cleared_requirements == f.read()
