import functools
from shared.common import *

def exception(func):
    """
    Decorator to catch exceptions and avoid stop script
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            message = "\nError running check {}. Error message {}".format(func.__qualname__, str(e))
            log_critical(message)
            pass
    return wrapper