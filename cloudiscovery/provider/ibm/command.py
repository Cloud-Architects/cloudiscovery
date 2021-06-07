from provider.ibm.vpc.command import Vpc
from shared.common import (
    exit_critical,
    BaseCommand,
)

DEFAULT_REGION = "us-south"


def ibm_main(args) -> BaseCommand:

    # Check if verbose mode is enabled

    # ibm profile check
    region_name = args.region_name

    if "region_name" not in args:
        region_name = [DEFAULT_REGION]

    if "url" not in args:
        url = "https://us-south.iaas.cloud.ibm.com"

    if "threshold" in args:
        if args.threshold is not None:
            if args.threshold.isdigit() is False:
                exit_critical("Threshold must be between 0 and 100")
            else:
                if int(args.threshold) < 0 or int(args.threshold) > 100:
                    exit_critical("Threshold must be between 0 and 100")

    if args.command == "ibm-vpc":
        command = Vpc(
            vpc_id=args.vpc_id,
            apikey=args.api_key,
            region=region_name,
            url=url,
        )
    else:
        raise NotImplementedError("Unknown command")
    return command
