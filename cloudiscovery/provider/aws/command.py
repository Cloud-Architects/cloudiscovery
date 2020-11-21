from provider.aws.all.command import All
from provider.aws.common_aws import generate_session, aws_verbose
from provider.aws.iot.command import Iot
from provider.aws.limit.command import Limit
from provider.aws.policy.command import Policy
from provider.aws.security.command import Security
from provider.aws.vpc.command import Vpc
from shared.common import (
    exit_critical,
    message_handler,
    BaseCommand,
)

DEFAULT_REGION = "us-east-1"
DEFAULT_PARTITION_CODE = "aws"


def get_partition(session, region_name):
    partition_code = DEFAULT_PARTITION_CODE  # assume it's always default partition, even if we can't find a region
    partition_name = "AWS Standard"
    # pylint: disable=protected-access
    loader = session._session.get_component("data_loader")
    endpoints = loader.load_data("endpoints")
    for partition in endpoints["partitions"]:
        for region, _ in partition["regions"].items():
            if region == region_name:
                partition_code = partition["partition"]
                partition_name = partition["partitionName"]

    if partition_code != DEFAULT_PARTITION_CODE:
        message_handler(
            "Found non-default partition: {} ({})".format(
                partition_code, partition_name
            ),
            "HEADER",
        )
    return partition_code


def check_region_profile(arg_region_name, profile_region_name):
    if arg_region_name is None and profile_region_name is None:
        exit_critical("Neither region parameter nor region config were passed")


def check_region(region_parameter, region_name, session, partition_code):
    """
    Region us-east-1 as a default region here, if not aws partition, just return asked region

    This is just to list aws regions, doesn't matter default region
    """
    if partition_code != "aws":
        return [region_name]

    client = session.client("ec2", region_name=DEFAULT_REGION)

    valid_region_names = [
        region["RegionName"]
        for region in client.describe_regions(AllRegions=True)["Regions"]
    ]

    if region_parameter != "all":
        if region_name not in valid_region_names:
            message = "There is no region named: {0}".format(region_name)
            exit_critical(message)
        else:
            valid_region_names = [region_name]

    return valid_region_names


def aws_main(args) -> BaseCommand:

    # Check if verbose mode is enabled
    if args.verbose:
        aws_verbose()

    # aws profile check
    if "region_name" not in args:
        session = generate_session(profile_name=args.profile_name, region_name=None)
    else:
        session = generate_session(
            profile_name=args.profile_name, region_name=args.region_name
        )

    session.get_credentials()
    region_name = session.region_name

    partition_code = get_partition(session, region_name)

    if "region_name" not in args:
        region_names = [DEFAULT_REGION]
    else:
        # checking region configuration
        check_region_profile(
            arg_region_name=args.region_name, profile_region_name=region_name
        )

        # assuming region parameter precedes region configuration
        if args.region_name is not None:
            region_name = args.region_name

        # get regions
        region_names = check_region(
            region_parameter=args.region_name,
            region_name=region_name,
            session=session,
            partition_code=partition_code,
        )

    if "threshold" in args:
        if args.threshold is not None:
            if args.threshold.isdigit() is False:
                exit_critical("Threshold must be between 0 and 100")
            else:
                if int(args.threshold) < 0 or int(args.threshold) > 100:
                    exit_critical("Threshold must be between 0 and 100")

    if args.command == "aws-vpc":
        command = Vpc(
            vpc_id=args.vpc_id,
            region_names=region_names,
            session=session,
            partition_code=partition_code,
        )
    elif args.command == "aws-policy":
        command = Policy(
            region_names=region_names, session=session, partition_code=partition_code
        )
    elif args.command == "aws-iot":
        command = Iot(
            thing_name=args.thing_name,
            region_names=region_names,
            session=session,
            partition_code=partition_code,
        )
    elif args.command == "aws-all":
        command = All(
            region_names=region_names, session=session, partition_code=partition_code
        )
    elif args.command == "aws-limit":
        command = Limit(
            region_names=region_names,
            session=session,
            threshold=args.threshold,
            partition_code=partition_code,
        )
    elif args.command == "aws-security":
        command = Security(
            region_names=region_names,
            session=session,
            commands=args.commands,
            partition_code=partition_code,
        )
    else:
        raise NotImplementedError("Unknown command")
    return command
