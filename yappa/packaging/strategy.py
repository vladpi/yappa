from yappa.packaging.direct import create_function_version_direct
from yappa.packaging.s3 import create_function_version_s3

CREATORS = {
    "s3": create_function_version_s3,
    "direct": create_function_version_direct,
}


def create_function_version(yc, config, strategy):
    creator = CREATORS[strategy]
    return creator(yc, config)
