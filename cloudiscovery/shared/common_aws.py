import botocore.exceptions
from cachetools import TTLCache

from provider.vpc.command import VpcOptions


SUBNET_CACHE = TTLCache(maxsize=1024, ttl=60)


def describe_subnet(vpc_options: VpcOptions, subnet_ids):
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
