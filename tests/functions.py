import pytest


@pytest.fixture(scope="session")
def uploaded_package():
    """
    load config
    upload package
    yield bucket name
    delete bucket
    """


@pytest.fixture
def function_name(faker):
    return faker.uuid4()


@pytest.fixture
def function(function_name, yc):
    function = yc.create_function(function_name)
    yield function
    yc.delete_function(function.id)


def test_function_list(yc):
    functions = yc.get_functions()
    assert isinstance(functions, dict)


def test_function_creation(yc, function_name):
    assert function_name not in yc.get_functions()
    function = yc.create_function(function_name)
    assert function.name == function_name
    assert function_name in yc.get_functions()
    yc.delete_function(function.id)
    assert function_name not in yc.get_functions()


def test_function_access(yc, function):
    assert yc.is_function_public(function.id) == True
    yc.set_access(function.id, is_public=False)
    assert yc.is_function_public(function.id) == False


def test_function_version(yc, function, uploaded_package):
    pass
