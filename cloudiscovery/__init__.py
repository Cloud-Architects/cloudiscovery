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

import gettext
import sys
from os.path import dirname
from typing import List

import pkg_resources

from provider.aws.command import aws_main
from shared.parameters import generate_parser

"""path to pip package"""
sys.path.append(dirname(__file__))

# pylint: disable=wrong-import-position
from shared.common import (
    exit_critical,
    Filterable,
    parse_filters,
)

# Check version
if sys.version_info < (3, 8):
    print("Python 3.8 or newer is required", file=sys.stderr)
    sys.exit(1)

__version__ = "2.4"

AVAILABLE_LANGUAGES = ["en_US", "pt_BR"]


# pylint: disable=too-many-branches,too-many-statements,too-many-locals
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

    if args.command.startswith("aws"):
        command = aws_main(args)
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


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Finishing script...")
        sys.exit(0)
