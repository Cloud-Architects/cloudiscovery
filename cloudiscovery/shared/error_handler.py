import functools
import platform
import traceback
import sys

from shared.common import log_critical


# Decorator to catch exceptions and avoid stop script.


def exception(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # pylint: disable=import-outside-toplevel
        from botocore.client import ClientError
        from botocore.exceptions import UnknownServiceError
        from boto3 import __version__ as boto3_version

        try:
            return func(*args, **kwargs)

        except ClientError as e:
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

        except UnknownServiceError:
            log_critical("You're running a possible out of date boto3 version.")
            log_critical("Please update boto3 to last version.")

            issue_info = "\n".join(
                (
                    "Python:        {0}".format(sys.version),
                    "boto3 version: {0}".format(boto3_version),
                    "Platform:      {0}".format(platform.platform()),
                    "",
                    traceback.format_exc(),
                )
            )
            log_critical(issue_info)

        except Exception:  # pylint: disable=broad-except
            log_critical("You've found a bug! Please, open an issue in GitHub project")
            log_critical("https://github.com/Cloud-Architects/cloudiscovery/issues\n")

            issue_info = "\n".join(
                (
                    "Python:        {0}".format(sys.version),
                    "boto3 version: {0}".format(boto3_version),
                    "Platform:      {0}".format(platform.platform()),
                    "",
                    traceback.format_exc(),
                )
            )
            log_critical(issue_info)

    return wrapper
