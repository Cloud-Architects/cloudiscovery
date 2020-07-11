from typing import List

from provider.limit.command import LimitOptions
from shared.common import ResourceProvider, Resource, ResourceDigest, LimitsValues
from shared.error_handler import exception


class SesResources(ResourceProvider):
    def __init__(self, options: LimitOptions):
        """
        SES resources

        :param options:
        """
        super().__init__()
        self.options = options

    @exception
    def get_resources(self) -> List[Resource]:

        services = self.options.services

        if "ses" not in services:
            return []

        client = self.options.client("ses")

        response = client.get_send_quota()
        max_send = response["Max24HourSend"]
        last_send = response["SentLast24Hours"]
        if max_send == -1:
            percent = "0"
        else:
            percent = round((last_send / max_send) * 100, 2)

        return [
            Resource(
                digest=ResourceDigest(id="ses-send-quota", type="aws_limit"),
                name="",
                group="",
                limits=LimitsValues(
                    quota_name="Sending limit for the Amazon SES account per day "
                    "(limit 200 can mean sandbox mode enabled)",
                    quota_code="ses-send-quota",
                    aws_limit=int(
                        200
                    ),  # https://forums.aws.amazon.com/thread.jspa?threadID=61090
                    local_limit=int(max_send),
                    usage=int(last_send),
                    service="ses",
                    percent=percent,
                ),
            )
        ]
