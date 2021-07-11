MIN_MEMORY, MAX_MEMORY = 134217728, 2147483648

SIZE_SUFFIXES = {
    'kb': 1024,
    'mb': 1024 * 1024,
    'gb': 1024 * 1024 * 1024,
}


def convert_size_to_bytes(size_str):
    for suffix in SIZE_SUFFIXES:
        if size_str.lower().endswith(suffix):
            size = int(size_str[0:-len(suffix)]) * SIZE_SUFFIXES[suffix]
            if not MIN_MEMORY <= size <= MAX_MEMORY:
                raise ValueError("Sorry. Due to YandexCloud limits, function "
                                 "memory should be between 128mB and 2GB")
            return size
    raise ValueError("Oops. Couldn't parse memory limit. "
                     "It should be in format 128MB, 2GB")


HANDLERS = {
    "wsgi": "handlers.wsgi.handle",
}


def get_yc_entrypoint(application_type):
    entrypoint = HANDLERS.get(application_type)
    if not entrypoint:
        raise ValueError(
            f"Sorry, supported app types are: {','.join(HANDLERS.keys())}."
        )
    return entrypoint
