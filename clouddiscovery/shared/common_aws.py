import botocore.exceptions

from provider.vpc.command import VpcOptions


def _describe_subnet(vpc_options: VpcOptions, subnets_id):

    ec2 = vpc_options.client("ec2")

    if not isinstance(subnets_id, list):
        subnets_id = [subnets_id]

    try:
        subnets = ec2.describe_subnets(SubnetIds=subnets_id)
        return subnets
    except botocore.exceptions.ClientError:
        return None
