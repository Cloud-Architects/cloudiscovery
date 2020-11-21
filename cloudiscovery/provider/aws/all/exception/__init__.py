import functools
from shared.common import (
    message_handler,
    log_critical,
)


def all_exception(func):
    # pylint: disable=inconsistent-return-statements
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        # pylint: disable=broad-except
        except Exception as e:
            if func.__qualname__ == "AllResources.analyze_operation":
                if not args[0].options.verbose:
                    return
                exception_str = str(e)
                if (
                    "is not subscribed to AWS Security Hub" in exception_str
                    or "not enabled for securityhub" in exception_str
                    or "The subscription does not exist" in exception_str
                    or "calling the DescribeHub operation" in exception_str
                ):
                    message_handler(
                        "Operation {} not accessible, AWS Security Hub is not configured... Skipping".format(
                            args[2]
                        ),
                        "WARNING",
                    )
                elif (
                    "not connect to the endpoint URL" in exception_str
                    or "not available in this region" in exception_str
                    or "API is not available" in exception_str
                ):
                    message_handler(
                        "Service {} not available in the selected region... Skipping".format(
                            args[5]
                        ),
                        "WARNING",
                    )
                elif (
                    "Your account is not a member of an organization" in exception_str
                    or "This action can only be made by accounts in an AWS Organization"
                    in exception_str
                    or "The request failed because organization is not in use"
                    in exception_str
                ):
                    message_handler(
                        "Service {} only available to account in an AWS Organization... Skipping".format(
                            args[5]
                        ),
                        "WARNING",
                    )
                elif "is no longer available to new customers" in exception_str:
                    message_handler(
                        "Service {} is no longer available to new customers... Skipping".format(
                            args[5]
                        ),
                        "WARNING",
                    )
                elif (
                    "only available to Master account in AWS FM" in exception_str
                    or "not currently delegated by AWS FM" in exception_str
                ):
                    message_handler(
                        "Operation {} not accessible, not master account in AWS FM... Skipping".format(
                            args[2]
                        ),
                        "WARNING",
                    )
                else:
                    log_critical(
                        "\nError running operation {}, type {}. Error message {}".format(
                            args[2], args[1], exception_str
                        )
                    )
            else:
                log_critical(
                    "\nError running method {}. Error message {}".format(
                        func.__qualname__, str(e)
                    )
                )

    return wrapper
