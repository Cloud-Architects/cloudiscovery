import botocore.exceptions
from cachetools import TTLCache

from shared.common import ResourceCache

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

        paths_found = []
        paths = self.parameters()
        for path in paths:
            paths_found.append(path["Value"])

        self.cache.set_key(key=cache_key, value=paths_found, expire=86400)
        return paths_found
