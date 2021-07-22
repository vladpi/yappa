import json
import os
import sys
from pathlib import Path

import pytest

from yappa.handlers.manage import manage


@pytest.fixture(scope="session", autouse=True)
def django_settings():
    os.environ["DJANGO_SETTINGS_MODULE"] = "django_settings"
    sys.path.append(
            str(Path(Path(__file__).resolve().parent.parent, "test_apps")))


def test_help():
    response = manage({"body": json.dumps({"command": "help", "args": []})})
    assert response["statusCode"] == 200
    assert response["body"].startswith("\nType 'python -m django")


def test_arguments():
    response = manage({"body": json.dumps({"command": "check", "args": []})})
    assert response["body"] == (
            'System check identified no issues (0 silenced).\n')
    response = manage(
            {"body": json.dumps({"command": "check", "args": ["--deploy"]})})
    assert response["body"].startswith("System check identified some issues")
