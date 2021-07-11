from furl import furl

DEFAULT_GW_CONFIG_FILENAME = "yappa_gw.yaml"
HANDLERS_DIR = "handlers"
DEFAULT_PACKAGE_DIR = "yappa_package"
DEFAULT_PROFILE_NAME = "default"
DEFAULT_REQUIREMENTS_FILE = "requirements.txt"
DEFAULT_ACCESS_KEY_FILE = ".yc"
DEFAULT_SERVICE_ACCOUNT = "yappa-uploader-service"
DEFAULT_IGNORED_FILES = (
    ".idea",
    ".git",
    "venv",
    "requirements.txt",
)
AVAILABLE_PYTHON_VERSIONS = (
    "python38",
    "python37",
)
YANDEX_S3_URL = 'https://storage.yandexcloud.net'
YANDEX_CLIENT_ID = "9878e3bd8f1e4bc292ee9c74bbc736a2"
YANDEX_OAUTH_URL = furl("https://oauth.yandex.ru/authorize").add({
    "response_type": "token",
    "client_id": YANDEX_CLIENT_ID,
}).url
