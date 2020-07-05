from typing import List

from concurrent.futures.thread import ThreadPoolExecutor

from provider.limit.command import LimitOptions, ALLOWED_SERVICES_CODES
from shared.common import (
    ResourceProvider,
    Resource,
    ResourceDigest,
    message_handler,
    ResourceCache,
    LimitsValues,
)
from shared.common_aws import get_paginator
from shared.error_handler import exception

SERVICEQUOTA_TO_BOTO3 = {
    "elasticloadbalancing": "elbv2",
    "elasticfilesystem": "efs",
}

MAX_EXECUTION_PARALLEL = 3


class LimitResources(ResourceProvider):
    def __init__(self, options: LimitOptions):
        """
        All resources

        :param options:
        """
        super().__init__()
        self.options = options
        self.cache = ResourceCache()

    @exception
    # pylint: disable=too-many-locals
    def get_resources(self) -> List[Resource]:

        threshold_requested = (
            0 if self.options.threshold is None else self.options.threshold
        )

        client_quota = self.options.session.client("service-quotas")

        resources_found = []

        services = self.options.services

        with ThreadPoolExecutor(MAX_EXECUTION_PARALLEL) as executor:
            results = executor.map(
                lambda aws_limit: self.analyze_service(
                    aws_limit=aws_limit,
                    client_quota=client_quota,
                    threshold_requested=int(threshold_requested),
                ),
                services,
            )

        for result in results:
            if result is not None:
                resources_found.extend(result)

        return resources_found

    @exception
    def analyze_service(self, aws_limit, client_quota, threshold_requested):

        service = aws_limit

        cache_key = "aws_limits_" + service + "_" + self.options.region_name
        cache = self.cache.get_key(cache_key)

        return self.analyze_detail(
            client_quota=client_quota,
            data_resource=cache[service],
            service=service,
            threshold_requested=threshold_requested,
        )

    @exception
    # pylint: disable=too-many-locals
    def analyze_detail(self, client_quota, data_resource, service, threshold_requested):

        resources_found = []

        for data_quota_code in data_resource:

            quota_data = ALLOWED_SERVICES_CODES[service][data_quota_code["quota_code"]]

            value_aws = value = data_quota_code["value"]

            # Quota is adjustable by ticket request, then must override this values.
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

            if self.options.verbose:
                message_handler(
                    "Collecting data from Quota: "
                    + service
                    + " - "
                    + data_quota_code["quota_name"]
                    + "...",
                    "HEADER",
                )

            # Need to convert some quota-services endpoint
            if service in SERVICEQUOTA_TO_BOTO3:
                service = SERVICEQUOTA_TO_BOTO3.get(service)

            client = self.options.session.client(
                service, region_name=self.options.region_name
            )

            usage = 0

            pages = get_paginator(
                client=client,
                operation_name=quota_data["method"],
                resource_type="aws_limit",
            )
            if not pages:
                response = getattr(client, quota_data["method"])()
                usage = len(response[quota_data["key"]])
            else:
                for page in pages:
                    usage = usage + len(page[quota_data["key"]])

            percent = round((usage / value) * 100, 2)

            if percent >= threshold_requested:
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
                            percent=percent,
                        ),
                    )
                )

        return resources_found
