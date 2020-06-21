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
            if "Could not connect to the endpoint URL" in str(e):
                message = "\nThe service {} is not available in this region".format(
                    func.__qualname__
                )
            else:
                message = "\nError running check {}. Error message {}".format(
                    func.__qualname__, str(e)
                )
            log_critical(message)

    return wrapper
