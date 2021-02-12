import argparse


def str2bool(v):
    if isinstance(v, bool):
        return v
    # pylint: disable=no-else-return
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


def generate_parser():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(help="commands", dest="command")

    # Begin AWS "aws" parser declarations
    aws_parser = subparsers.add_parser("aws", help="aws help")
    aws_subparser = aws_parser.add_subparsers(title="AWS Discovery", dest="resource")

    aws_vpc_parser = aws_subparser.add_parser("vpc", help="aws vpc help")
    add_default_arguments(aws_vpc_parser)
    aws_vpc_parser.add_argument(
        "-v",
        "--vpc-id",
        required=False,
        help="Inform VPC to analyze. If not informed, script will check all vpcs.",
    )

    aws_iot_parser = aws_subparser.add_parser("iot", help="aws iot help")
    add_default_arguments(aws_iot_parser)
    aws_iot_parser.add_argument(
        "-t",
        "--thing-name",
        required=False,
        help="Inform Thing Name to analyze. If not informed, script will check all things inside a region.",
    )

    aws_policy_parser = aws_subparser.add_parser("policy", help="aws policy help")
    add_default_arguments(aws_policy_parser, is_global=True)

    aws_all_parser = aws_subparser.add_parser("all", help="aws all help")
    add_default_arguments(aws_all_parser, diagram_enabled=False)
    add_services_argument(aws_all_parser)

    aws_limit_parser = aws_subparser.add_parser("limit", help="aws limit help")
    add_default_arguments(
        aws_limit_parser, diagram_enabled=False, filters_enabled=False
    )
    add_services_argument(aws_limit_parser)
    aws_limit_parser.add_argument(
        "-t",
        "--threshold",
        required=False,
        help="Select the %% of resource threshold between 0 and 100. \
              For example: --threshold 50 will report all resources with more than 50%% threshold.",
    )

    aws_security_parser = aws_subparser.add_parser("security", help="aws security help")
    add_default_arguments(
        aws_security_parser, diagram_enabled=False, filters_enabled=False
    )
    aws_security_parser.add_argument(
        "-c",
        "--commands",
        action="append",
        required=False,
        help='Select the security check command that you want to run. \
              To see available commands, please type "-c list". \
              If not passed, command will check all services.',
    )

    # Begin Azure "az" parser declaration
    az_parser = subparsers.add_parser("az", help="az help")
    az_subparser = az_parser.add_subparsers(title="Azure Discovery", dest="resource")

    az_all_parser = az_subparser.add_parser("all", help="az all help")
    add_default_arguments(az_all_parser, diagram_enabled=False)
    add_services_argument(az_all_parser)

    return parser


def add_services_argument(limit_parser):
    limit_parser.add_argument(
        "-s",
        "--services",
        required=False,
        help='Define services that you want to check, use "," (comma) to separate multiple names. \
              If not passed, command will check all services.',
    )


def add_default_arguments(
    parser, is_global=False, diagram_enabled=True, filters_enabled=True
):
    if not is_global:
        parser.add_argument(
            "-r",
            "--region-name",
            required=False,
            help='Inform REGION NAME to analyze or "all" to check on all regions. \
            If not informed, try to get from config file',
        )
    parser.add_argument(
        "-p", "--profile-name", required=False, help="Profile to be used"
    )
    parser.add_argument(
        "-l", "--language", required=False, help="Available languages: pt_BR, en_US"
    )
    parser.add_argument(
        "--verbose",
        "--verbose",
        type=str2bool,
        nargs="?",
        const=True,
        default=False,
        help="Enable debug mode to sdk calls (default false)",
    )
    if filters_enabled:
        parser.add_argument(
            "-f",
            "--filters",
            action="append",
            required=False,
            help="filter resources (tags only for now, you must specify name and values); multiple filters "
            "are possible to pass with -f <filter_1> -f <filter_2> approach, values can be separated by : sign; "
            "example: Name=tags.costCenter;Value=20000:'20001:1'",
        )
    if diagram_enabled:
        parser.add_argument(
            "-d",
            "--diagram",
            type=str2bool,
            nargs="?",
            const=True,
            default=True,
            help="print diagram with resources (need Graphviz installed). Pass true/y[es] to "
            "view image or false/n[o] not to generate image. Default true",
        )
