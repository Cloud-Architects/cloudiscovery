import botocore.exceptions
from cachetools import TTLCache

from shared.common import ResourceCache, message_handler
from provider.limits.resource.all import ALLOWED_SERVICES_CODES

SUBNET_CACHE = TTLCache(maxsize=1024, ttl=60)


def describe_subnet(vpc_options, subnet_ids):
    if not isinstance(subnet_ids, list):
        subnet_ids = [subnet_ids]

    if str(subnet_ids) in SUBNET_CACHE:
        return SUBNET_CACHE[str(subnet_ids)]

    ec2 = vpc_options.client("ec2")
    try:
        subnets = ec2.describe_subnets(SubnetIds=subnet_ids)
        SUBNET_CACHE[str(subnet_ids)] = subnets
        return subnets
    except botocore.exceptions.ClientError:
        return None


class LimitParameters:
    def __init__(self, session, region: str, services):
        self.region = region
        self.cache = ResourceCache()
        self.session = session
        self.services = []
        if services is None:
            for service in ALLOWED_SERVICES_CODES:
                self.services.append(service)
        else:
            self.services = services

    def init_globalaws_limits_cache(self):
        """
        AWS has global limits that can be adjustable and others that can't be adjustable
        This method make cache for 15 days for aws cache global parameters. AWS don't update limits every time.
        Services has differents limits, depending on region.
        """
        for service_code in self.services:
            if service_code in ALLOWED_SERVICES_CODES:
                cache_key = "aws_limits_" + service_code + "_" + self.region

                cache = self.cache.get_key(cache_key)
                if cache is not None:
                    continue

                message_handler(
                    "Fetching aws global limits to service {} in region {} to cache...".format(
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

                        response = service_quota.get_aws_default_service_quota(
                            ServiceCode=service_code, QuotaCode=quota_code
                        )

                        item_to_add = {
                            "value": response["Quota"]["Value"],
                            "adjustable": response["Quota"]["Adjustable"],
                            "quota_code": quota_code,
                            "quota_name": response["Quota"]["QuotaName"],
                        }

                        if service_code in cache_codes:
                            cache_codes[service_code].append(item_to_add)
                        else:
                            cache_codes[service_code] = [item_to_add]

                self.cache.set_key(key=cache_key, value=cache_codes, expire=1296000)

        return True


class GlobalParameters:
    def __init__(self, session, region: str, path: str):
        self.region = region
        self.session = session.client("ssm", region_name="us-east-1")
        self.path = path
        self.cache = ResourceCache()

    def get_parameters_by_path(self, next_token=None):

        params = {"Path": self.path, "Recursive": True, "MaxResults": 10}
        if next_token is not None:
            params["NextToken"] = next_token

        return self.session.get_parameters_by_path(**params)

    def parameters(self):
        next_token = None
        while True:
            response = self.get_parameters_by_path(next_token)
            parameters = response["Parameters"]
            if not parameters:
                break
            for parameter in parameters:
                yield parameter
            if "NextToken" not in response:
                break
            next_token = response["NextToken"]

    def paths(self):

        cache_key = "aws_paths_" + self.region
        cache = self.cache.get_key(cache_key)

        if cache is not None:
            return cache

        message_handler(
            "Fetching available resources in region {} to cache...".format(self.region),
            "HEADER",
        )
        paths_found = []
        paths = self.parameters()
        for path in paths:
            paths_found.append(path["Value"])

        self.cache.set_key(key=cache_key, value=paths_found, expire=86400)
        return paths_found
