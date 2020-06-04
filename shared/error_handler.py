import functools

from shared.common import log_critical


def exception(func):
    """
    Decorator to catch exceptions and avoid stop script
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
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
            pass

    return wrapper
