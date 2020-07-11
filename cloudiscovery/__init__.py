#!/usr/bin/env python3
"""
Licensed under the Apache License, Version 2.0 (the "License");

you may not use this file except in compliance with the License.
You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import argparse
import gettext
import sys
from os.path import dirname
from typing import List

import pkg_resources

"""path to pip package"""
sys.path.append(dirname(__file__))

# pylint: disable=wrong-import-position

from provider.policy.command import Policy
from provider.vpc.command import Vpc
from provider.iot.command import Iot
from provider.all.command import All
from provider.limit.command import Limit

from shared.common import (
    exit_critical,
    Filterable,
    parse_filters,
)
from shared.common_aws import aws_verbose, generate_session

# pylint: enable=wrong-import-position
# Check version
if sys.version_info < (3, 6):
    print("Python 3.6 or newer is required", file=sys.stderr)
    sys.exit(1)

__version__ = "2.2.3"

AVAILABLE_LANGUAGES = ["en_US", "pt_BR"]
DEFAULT_REGION = "us-east-1"


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

    vpc_parser = subparsers.add_parser("aws-vpc", help="Analyze VPCs")
    add_default_arguments(vpc_parser)
    vpc_parser.add_argument(
        "-v",
        "--vpc-id",
        required=False,
        help="Inform VPC to analyze. If not informed, script will check all vpcs.",
    )

    iot_parser = subparsers.add_parser("aws-iot", help="Analyze IoTs")
    add_default_arguments(iot_parser)
    iot_parser.add_argument(
        "-t",
        "--thing-name",
        required=False,
        help="Inform Thing Name to analyze. If not informed, script will check all things inside a region.",
    )

    policy_parser = subparsers.add_parser("aws-policy", help="Analyze policies")
    add_default_arguments(policy_parser, is_global=True)

    all_parser = subparsers.add_parser("aws-all", help="Analyze all resources")
    add_default_arguments(all_parser, diagram_enabled=False)
    add_services_argument(all_parser)

    limit_parser = subparsers.add_parser(
        "aws-limit", help="Analyze aws limit resources."
    )
    add_default_arguments(limit_parser, diagram_enabled=False, filters_enabled=False)
    add_services_argument(limit_parser)
    limit_parser.add_argument(
        "-t",
        "--threshold",
        required=False,
        help="Select the %% of resource threshold between 0 and 100. \
              For example: --threshold 50 will report all resources with more than 50%% threshold.",
    )

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


# pylint: disable=too-many-branches,too-many-statements
def main():
    # Entry point for the CLI.
    # Load commands
    parser = generate_parser()
    if len(sys.argv) <= 1:
        parser.print_help()
        return

    args = parser.parse_args()

    # Check if verbose mode is enabled
    if args.verbose:
        aws_verbose()

    if args.language is None or args.language not in AVAILABLE_LANGUAGES:
        language = "en_US"
    else:
        language = args.language

    # Diagram check
    if "diagram" not in args:
        diagram = False
    else:
        diagram = args.diagram

    # defining default language to show messages
    defaultlanguage = gettext.translation(
        "messages", localedir=dirname(__file__) + "/locales", languages=[language]
    )
    defaultlanguage.install()
    _ = defaultlanguage.gettext

    # diagram version check
    check_diagram_version(diagram)

    # filters check
    filters: List[Filterable] = []
    if "filters" in args:
        if args.filters is not None:
            filters = parse_filters(args.filters)

    # aws profile check
    if "region_name" not in args:
        session = generate_session(profile_name=args.profile_name, region_name=None)
    else:
        session = generate_session(
            profile_name=args.profile_name, region_name=args.region_name
        )

    session.get_credentials()
    region_name = session.region_name

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
            region_parameter=args.region_name, region_name=region_name, session=session,
        )

    if "threshold" in args:
        if args.threshold is not None:
            if args.threshold.isdigit() is False:
                exit_critical(_("Threshold must be between 0 and 100"))
            else:
                if int(args.threshold) < 0 or int(args.threshold) > 100:
                    exit_critical(_("Threshold must be between 0 and 100"))

    if args.command == "aws-vpc":
        command = Vpc(vpc_id=args.vpc_id, region_names=region_names, session=session,)
    elif args.command == "aws-policy":
        command = Policy(region_names=region_names, session=session,)
    elif args.command == "aws-iot":
        command = Iot(
            thing_name=args.thing_name, region_names=region_names, session=session,
        )
    elif args.command == "aws-all":
        command = All(region_names=region_names, session=session)
    elif args.command == "aws-limit":
        command = Limit(
            region_names=region_names, session=session, threshold=args.threshold,
        )
    else:
        raise NotImplementedError("Unknown command")
    if "services" in args and args.services is not None:
        services = args.services.split(",")
    else:
        services = []
    command.run(diagram, args.verbose, services, filters)


def check_diagram_version(diagram):
    if diagram:
        # Checking diagram version. Must be 0.13 or higher
        if pkg_resources.get_distribution("diagrams").version < "0.14":
            exit_critical(
                "You must update diagrams package to 0.14 or higher. "
                "- See on https://github.com/mingrammer/diagrams"
            )


def check_region_profile(arg_region_name, profile_region_name):

    if arg_region_name is None and profile_region_name is None:
        exit_critical("Neither region parameter nor region config were passed")


def check_region(region_parameter, region_name, session):
    """
    Region us-east-1 as a default region here

    This is just to list aws regions, doesn't matter default region
    """
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


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Finishing script...")
        sys.exit(0)
