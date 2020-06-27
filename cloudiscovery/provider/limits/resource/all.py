from typing import List

from shared.common_aws import ALLOWED_SERVICES_CODES
from shared.common import (
    ResourceProvider,
    Resource,
    BaseAwsOptions,
    ResourceDigest,
    message_handler,
    ResourceCache,
)
from shared.error_handler import exception


class LimitResources(ResourceProvider):
    def __init__(self, options: BaseAwsOptions):
        """
        All resources

        :param options:
        """
        super().__init__()
        self.options = options
        self.cache = ResourceCache()

    @exception
    def get_resources(self) -> List[Resource]:

        client_quota = self.options.session.client("service-quotas")

        resources_found = []

        services = self.options.services.split(",")
        for service in services:
            cache_key = "aws_limits_" + service + "_" + self.options.region_name
            cache = self.cache.get_key(cache_key)

            for data_quota_code in cache[service]:
                quota_data = ALLOWED_SERVICES_CODES[service][
                    data_quota_code["quota_code"]
                ]

                # Quota is adjustable by ticket request, then must override this values
                if bool(data_quota_code["adjustable"]) is True:
                    response_quota = client_quota.get_service_quota(
                        ServiceCode=service, QuotaCode=data_quota_code["quota_code"]
                    )
                    if "Value" in response_quota["Quota"]:
                        value = response_quota["Quota"]["Value"]
                    else:
                        value = data_quota_code["value"]

                message_handler(
                    "Collecting data from Quota: "
                    + data_quota_code["quota_name"]
                    + "...",
                    "HEADER",
                )
                client = self.options.session.client(service)

                response = getattr(client, quota_data["method"])()

                total = str(len(response[quota_data["key"]]))

                resources_found.append(
                    Resource(
                        digest=ResourceDigest(
                            id=data_quota_code["quota_code"], type="aws_limit"
                        ),
                        name=data_quota_code["quota_name"],
                        group=service,
                        details="Limit: "
                        + str(int(value))
                        + "... Current usage: "
                        + total,
                    )
                )

        return resources_found
