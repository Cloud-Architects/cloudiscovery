from typing import List

from shared.common_aws import ALLOWED_SERVICES_CODES
from shared.common import (
    ResourceProvider,
    Resource,
    BaseAwsOptions,
    ResourceDigest,
    message_handler,
    ResourceCache,
    LimitsValues,
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

        services = self.options.services

        for service in services:
            cache_key = "aws_limits_" + service + "_" + self.options.region_name
            cache = self.cache.get_key(cache_key)

            for data_quota_code in cache[service]:
                quota_data = ALLOWED_SERVICES_CODES[service][
                    data_quota_code["quota_code"]
                ]

                value_aws = data_quota_code["value"]

                # Quota is adjustable by ticket request, then must override this values
                if bool(data_quota_code["adjustable"]) is True:
                    try:
                        response_quota = client_quota.get_service_quota(
                            ServiceCode=service, QuotaCode=data_quota_code["quota_code"]
                        )
                        if "Value" in response_quota["Quota"]:
                            value = response_quota["Quota"]["Value"]
                        else:
                            value = data_quota_code["value"]
                    except client_quota.exceptions.NoSuchResourceException:
                        value = data_quota_code["value"]

                message_handler(
                    "Collecting data from Quota: "
                    + service
                    + " - "
                    + data_quota_code["quota_name"]
                    + "...",
                    "HEADER",
                )

                """
                TODO: Add this as alias to convert service name
                """
                if service == "elasticloadbalancing":
                    service = "elbv2"

                client = self.options.session.client(
                    service, region_name=self.options.region_name
                )

                response = getattr(client, quota_data["method"])()

                usage = len(response[quota_data["key"]])

                resources_found.append(
                    Resource(
                        digest=ResourceDigest(
                            id=data_quota_code["quota_code"], type="aws_limit"
                        ),
                        name="",
                        group="",
                        limits=LimitsValues(
                            quota_name=data_quota_code["quota_name"],
                            quota_code=data_quota_code["quota_code"],
                            aws_limit=int(value_aws),
                            local_limit=int(value),
                            usage=int(usage),
                            service=service,
                        ),
                    )
                )

        return resources_found
