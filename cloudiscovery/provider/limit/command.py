from typing import List

from shared.common import (
    ResourceCache,
    message_handler,
    Filterable,
    BaseOptions,
    log_critical,
)
from shared.common_aws import BaseAwsOptions, BaseAwsCommand, AwsCommandRunner
from shared.diagram import NoDiagram
from provider.limit.data.allowed_resources import (
    ALLOWED_SERVICES_CODES,
    SPECIAL_RESOURCES,
)


class LimitOptions(BaseAwsOptions, BaseOptions):
    services: List[str]
    threshold: str

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        verbose: bool,
        filters: List[Filterable],
        session,
        region_name,
        services,
        threshold,
    ):
        BaseAwsOptions.__init__(self, session, region_name)
        BaseOptions.__init__(self, verbose, filters)
        self.services = services
        self.threshold = threshold


class LimitParameters:
    def __init__(self, session, region: str, services, options: LimitOptions):
        self.region = region
        self.cache = ResourceCache()
        self.session = session
        self.options = options
        self.services = []

        if services is None:
            for service in ALLOWED_SERVICES_CODES:
                self.services.append(service)
            for service in SPECIAL_RESOURCES:
                self.services.append(service)
        else:
            self.services = services

    def init_globalaws_limits_cache(self):
        """
        AWS has global limit that can be adjustable and others that can't be adjustable
        This method make cache for 15 days for aws cache global parameters. AWS don't update limit every time.
        Services has differents limit, depending on region.
        """
        for service_code in self.services:
            if service_code in ALLOWED_SERVICES_CODES:
                cache_key = "aws_limits_" + service_code + "_" + self.region

                cache = self.cache.get_key(cache_key)
                if cache is not None:
                    continue

                if self.options.verbose:
                    message_handler(
                        "Fetching aws global limit to service {} in region {} to cache...".format(
                            service_code, self.region
                        ),
                        "HEADER",
                    )

                cache_codes = dict()
                for quota_code in ALLOWED_SERVICES_CODES[service_code]:

                    if quota_code != "global":
                        """
                        Impossible to instance once at __init__ method.
                        Global services such route53 MUST USE us-east-1 region
                        """
                        if ALLOWED_SERVICES_CODES[service_code]["global"]:
                            service_quota = self.session.client(
                                "service-quotas", region_name="us-east-1"
                            )
                        else:
                            service_quota = self.session.client(
                                "service-quotas", region_name=self.region
                            )

                        item_to_add = self.get_quota(
                            quota_code, service_code, service_quota
                        )
                        if item_to_add is None:
                            continue

                        if service_code in cache_codes:
                            cache_codes[service_code].append(item_to_add)
                        else:
                            cache_codes[service_code] = [item_to_add]

                self.cache.set_key(key=cache_key, value=cache_codes, expire=1296000)

        return True

    def get_quota(self, quota_code, service_code, service_quota):
        try:
            response = service_quota.get_aws_default_service_quota(
                ServiceCode=service_code, QuotaCode=quota_code
            )
        # pylint: disable=broad-except
        except Exception as e:
            if self.options.verbose:
                log_critical(
                    "\nCannot take quota {} for {}: {}".format(
                        quota_code, service_code, str(e)
                    )
                )
            return None
        item_to_add = {
            "value": response["Quota"]["Value"],
            "adjustable": response["Quota"]["Adjustable"],
            "quota_code": quota_code,
            "quota_name": response["Quota"]["QuotaName"],
        }
        return item_to_add


class Limit(BaseAwsCommand):
    def __init__(self, region_names, session, threshold):
        """
        All AWS resources

        :param region_names:
        :param session:
        :param threshold:
        """
        super().__init__(region_names, session)
        self.threshold = threshold

    def init_globalaws_limits_cache(self, region, services, options: LimitOptions):
        # Cache services global and local services
        LimitParameters(
            session=self.session, region=region, services=services, options=options
        ).init_globalaws_limits_cache()

    def run(
        self,
        diagram: bool,
        verbose: bool,
        services: List[str],
        filters: List[Filterable],
    ):
        if not services:
            services = []
            for service in ALLOWED_SERVICES_CODES:
                services.append(service)
            for service in SPECIAL_RESOURCES:
                services.append(service)

        for region in self.region_names:
            limit_options = LimitOptions(
                verbose=verbose,
                filters=filters,
                session=self.session,
                region_name=region,
                services=services,
                threshold=self.threshold,
            )
            self.init_globalaws_limits_cache(
                region=region, services=services, options=limit_options
            )

            command_runner = AwsCommandRunner(services=services)
            command_runner.run(
                provider="limit",
                options=limit_options,
                diagram_builder=NoDiagram(),
                title="AWS Limits - Region {}".format(region),
                # pylint: disable=no-member
                filename=limit_options.resulting_file_name("limit"),
            )
