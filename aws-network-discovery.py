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

# Check version
if sys.version_info < (3, 6):
    print("Python 3.6 or newer is required", file=sys.stderr)
    sys.exit(1)


from commands.vpc import Vpc

__version__ = "0.0.1"

def show_options(args="sys.argv[1:]"):
    parser = argparse.ArgumentParser()
    parser.add_argument(
                        "-v", 
                        "--vpc-id", 
                        required=True, 
                        help="Inform VPC to analyze"
                        )
    parser.add_argument(
                        "-r", 
                        "--region-name", 
                        required=False, 
                        help="Inform REGION to analyze. If not informed, try to get from config file"
                        )
    options = parser.parse_args()

    return options


def main():
    """Entry point for the CLI."""

    # Load commands
    if len(sys.argv) <= 1:
        options = show_options(args=['-h'])

    args = show_options(sys.argv)

    vpc = Vpc(vpc_id=args.vpc_id, region_name=args.region_name)
    vpc.run()


if __name__ == "__main__":
    main()