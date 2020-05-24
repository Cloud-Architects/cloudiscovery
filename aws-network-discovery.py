#!/usr/bin/env python3
"""
Copyright 2020 Conversando Na Nuvem (https://www.youtube.com/channel/UCuI2nDGLq_yjY9JNsDYStMQ/) - Leandro Damascena

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
following disclaimer in the documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote
products derived from this software without specific prior written permission.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
---------------------------------------------------------------------------

This script manages aws-network-discovery, a tool for analyzing VPC dependencies.
"""
import sys
import argparse
import gettext

# Check version
if sys.version_info < (3, 6):
    print(_("Python 3.6 or newer is required"), file=sys.stderr)
    sys.exit(1)


from commands.vpc import Vpc

__version__ = "0.7.0"

AVAILABLE_LANGUAGES = ['en_US','pt_BR']

def show_options(args="sys.argv[1:]"):
    parser = argparse.ArgumentParser()
    parser.add_argument(
                        "-v",
                        "--vpc-id",
                        required=False,
                        help="Inform VPC to analyze. If not informed, script try all vpcs."
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


    """ defining default language to show messages """
    defaultlanguage = gettext.translation('messages', localedir='locales', languages=[language])
    defaultlanguage.install()
    _ = defaultlanguage.gettext 


    vpc = Vpc(vpc_id=args.vpc_id, region_name=args.region_name, profile_name=args.profile_name)
    vpc.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('Finishing script...')
        sys.exit(0)