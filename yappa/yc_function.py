def create_function(name, description) -> str:
    """
    returns function id
    """
    pass


def set_access(function_name, is_anauthorized=True):
    pass


def update_function(function_id: str, description: str, bucket_name: str,
                    service_account_id: str,
                    **env) -> str:
    pass


def show_status(function_name):
    pass


def show_logs(function_name, since, until):
    pass


def delete_function(function_id):
    pass
