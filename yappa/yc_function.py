def create_function(name, description):
    """
    returns function id
    """
    pass


def get_function_id(name) -> str:
    pass


def set_access(function_name, is_unauthorized=True):
    pass


def update_function(function_id: str, description: str, bucket_name: str,
                    service_account_id: str, **env) -> str:
    pass


def show_status(function_name):
    pass


def show_logs(function_name, since, until):
    pass


def delete_function(function_id):
    pass
