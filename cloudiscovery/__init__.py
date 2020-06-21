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

# Check version
from shared.common import (
    exit_critical,
    generate_session,
    Filterable,
    parse_filters,
)

# pylint: enable=wrong-import-position

if sys.version_info < (3, 6):
    print("Python 3.6 or newer is required", file=sys.stderr)
    sys.exit(1)

__version__ = "2.1.1"

AVAILABLE_LANGUAGES = ["en_US", "pt_BR"]
DIAGRAMS_OPTIONS = ["True", "False"]
DEFAULT_REGION = "us-east-1"


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

    return parser


def add_default_arguments(parser, is_global=False):
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
        "-l", "--language", required=False, help="available languages: pt_BR, en_US"
    )
    parser.add_argument(
        "-f",
        "--filters",
        action="append",
        required=False,
        help="filter resources (tags only for now, you must specify name and values); multiple filters are possible "
        "to pass with -f <filter_1> -f <filter_2> approach, values can be separated by : sign; "
        "example: Name=tags.costCenter;Value=20000:'20001:1'",
    )
    parser.add_argument(
        "-d",
        "--diagram",
        required=False,
        help='print diagram with resources (need Graphviz installed). Use options "True" to '
        'view image or "False" to save image to disk. Default True',
    )


# pylint: disable=too-many-branches
def main():
    # Entry point for the CLI.
    # Load commands
    parser = generate_parser()
    if len(sys.argv) <= 1:
        parser.print_help()
        return

    args = parser.parse_args()

    if args.language is None or args.language not in AVAILABLE_LANGUAGES:
        language = "en_US"
    else:
        language = args.language

    # Diagram check
    if args.diagram is not None and args.diagram not in DIAGRAMS_OPTIONS:
        diagram = "True"
    else:
        diagram = args.diagram

    # defining default language to show messages
    defaultlanguage = gettext.translation(
        "messages", localedir=dirname(__file__) + "/locales", languages=[language]
    )
    defaultlanguage.install()
    _ = defaultlanguage.gettext

    # diagram version check
    if diagram:
        # Checking diagram version. Must be 0.13 or higher
        if pkg_resources.get_distribution("diagrams").version < "0.14":
            exit_critical(
                _(
                    "You must update diagrams package to 0.14 or higher. "
                    "- See on https://github.com/mingrammer/diagrams"
                )
            )

    # filters check
    filters: List[Filterable] = []
    if args.filters is not None:
        filters = parse_filters(args.filters)

    # aws profile check
    session = generate_session(args.profile_name)
    session.get_credentials()
    region_name = session.region_name

    if "region_name" not in args:
        region_names = [DEFAULT_REGION]
    else:
        if args.region_name is None and region_name is None:
            exit_critical(_("Neither region parameter or region config were informed"))

        # assuming region parameter precedes region configuration
        if args.region_name is not None:
            region_name = args.region_name

        # get regions
        region_names = check_region(
            region_parameter=args.region_name, region_name=region_name, session=session
        )

    if args.command == "aws-vpc":
        command = Vpc(
            vpc_id=args.vpc_id,
            region_names=region_names,
            session=session,
            diagram=diagram,
            filters=filters,
        )
    elif args.command == "aws-policy":
        command = Policy(
            region_names=region_names, session=session, diagram=diagram, filters=filters
        )
    elif args.command == "aws-iot":
        command = Iot(
            thing_name=args.thing_name,
            region_names=region_names,
            session=session,
            diagram=diagram,
            filters=filters,
        )
    else:
        raise NotImplementedError("Unknown command")
    command.run()


def check_region(region_parameter, region_name, session):
    """
    Region us-east-1 as a default region here

    This is just to list aws regions, doesn't matter default region
    """
    client = session.client("ec2", region_name=DEFAULT_REGION)

    valid_region_names = [
        region["RegionName"] for region in client.describe_regions()["Regions"]
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
