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

This script manages aws-network-discovery, a tool for analyzing VPC dependencies.
"""
import argparse
import gettext
import sys

# Check version
if sys.version_info < (3, 6):
    print(_("Python 3.6 or newer is required"), file=sys.stderr)
    sys.exit(1)

from commands.vpc import Vpc

__version__ = "0.8.0"

AVAILABLE_LANGUAGES = ['en_US', 'pt_BR']
DIAGRAMS_OPTIONS = ['True', 'False']


def show_options(args="sys.argv[1:]"):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v",
        "--vpc-id",
        required=False,
        help="Inform VPC to analyze. If not informed, script will check all vpcs."
    )
    parser.add_argument(
        "-r",
        "--region-name",
        required=False,
        help="Inform REGION to analyze. If not informed, try to get from config file"
    )
    parser.add_argument(
        "-p",
        "--profile-name",
        required=False,
        help="Profile to be used"
    )
    parser.add_argument(
        "-l",
        "--language",
        required=False,
        help="available languages: pt_BR, en_US"
    )
    parser.add_argument(
        "-d",
        "--diagram",
        required=False,
        help="print diagram with resources (need Graphviz installed). Use options \"True\" to " \
             "view image or \"False\" to save image to disk. Default True"
    )
    args = parser.parse_args()

    return args


def main():
    """Entry point for the CLI."""

    # Load commands
    if len(sys.argv) <= 1:
        options = show_options(args=['-h'])

    args = show_options(sys.argv)

    if args.language is None or args.language not in AVAILABLE_LANGUAGES:
        language = "en_US"
    else:
        language = args.language

    """ Diagram check """
    if args.diagram is not None and args.diagram not in DIAGRAMS_OPTIONS:
        diagram = "True"
    else:
        diagram = args.diagram

    """ defining default language to show messages """
    defaultlanguage = gettext.translation('messages', localedir='locales', languages=[language])
    defaultlanguage.install()
    _ = defaultlanguage.gettext

    vpc = Vpc(vpc_id=args.vpc_id,
              region_name=args.region_name,
              profile_name=args.profile_name,
              diagram=diagram)
    vpc.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('Finishing script...')
        sys.exit(0)
