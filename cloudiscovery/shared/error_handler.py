import functools

from shared.common import log_critical


# Decorator to catch exceptions and avoid stop script.
def exception(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        # pylint: disable=broad-except
        except Exception as e:
            exception_str = str(e)
            if (
                "Could not connect to the endpoint URL" in exception_str
                or "the specified service does not exist" in exception_str
            ):
                message = "\nThe service {} is not available in this region".format(
                    func.__qualname__
                )
            else:
                message = "\nError running check {}. Error message {}".format(
                    func.__qualname__, exception_str
                )
            log_critical(message)

    return wrapper
