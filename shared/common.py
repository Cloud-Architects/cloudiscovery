import datetime
import re
from typing import NamedTuple

import boto3
from ipaddress import ip_network

VPCE_REGEX = re.compile(r'(?<=sourcevpce")(\s*:\s*")(vpce-[a-zA-Z0-9]+)', re.DOTALL)
SOURCE_IP_ADDRESS_REGEX = re.compile(r'(?<=sourceip")(\s*:\s*")([a-fA-F0-9.:/%]+)', re.DOTALL)


class bcolors:
    colors = {'HEADER': '\033[95m',
              'OKBLUE': '\033[94m',
              'OKGREEN': '\033[92m',
              'WARNING': '\033[93m',
              'FAIL': '\033[91m',
              'ENDC': '\033[0m',
              'BOLD': '\033[1m',
              'UNDERLINE': '\033[4m'}


class VpcOptions(NamedTuple):
    session: boto3.Session
    vpc_id: str
    region_name: str

    def client(self, service_name: str):
        return self.session.client(service_name, region_name=self.region_name)


class Resource(NamedTuple):
    id: str
    name: str
    type: str
    details: str
    group: str


def get_name_tags(d):
    for k, v in d.items():
        if isinstance(v, dict):
            get_name_tags(v)
        else:
            if k == "Tags":
                for value in v:
                    if value["Key"] == 'Name':
                        return value["Value"]

    return False


def generate_session(profile_name):
    try:
        return boto3.Session(profile_name=profile_name)
    except Exception as e:
        message = "You must configure awscli before use this script.\nError: {0}".format(str(e))
        exit_critical(message)


def exit_critical(message):
    log_critical(message)
    raise SystemExit


def log_critical(message):
    print(bcolors.colors.get('FAIL'), message, bcolors.colors.get('ENDC'), sep="")


def message_handler(message, position):
    print(bcolors.colors.get(position), message, bcolors.colors.get('ENDC'), sep="")


def datetime_to_string(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()


def check_ipvpc_inpolicy(document, vpc_options: VpcOptions):
    document = document.replace("\\", "").lower()

    """ Checking if VPC is inside document, it's a 100% true information """
    if vpc_options.vpc_id in document:
        return "direct VPC reference"
    else:
        """ 
        Vpc_id not found, trying to discover if it's a potencial subnet IP or VPCE is allowed
        """
        if "aws:sourcevpce" in document:

            """ Get VPCE found """
            aws_sourcevpces = []
            for vpce_tuple in VPCE_REGEX.findall(document):
                aws_sourcevpces.append(vpce_tuple[1])

            """ Get all VPCE of this VPC """
            ec2 = vpc_options.client('ec2')

            filters = [{'Name': 'vpc-id',
                        'Values': [vpc_options.vpc_id]}]

            vpc_endpoints = ec2.describe_vpc_endpoints(Filters=filters)

            """ iterate VPCEs found found """
            if len(vpc_endpoints['VpcEndpoints']) > 0:
                matching_vpces = []
                """ Iterate VPCE to match vpce in Policy Document """
                for data in vpc_endpoints['VpcEndpoints']:
                    if data['VpcEndpointId'] in aws_sourcevpces:
                        matching_vpces.append(data['VpcEndpointId'])
                return "VPC Endpoint(s): " + (", ".join(matching_vpces))

        if "aws:sourceip" in document:

            """ Get ip found """
            aws_sourceips = []
            for vpce_tuple in SOURCE_IP_ADDRESS_REGEX.findall(document):
                aws_sourceips.append(vpce_tuple[1])
            """ Get subnets cidr block """
            ec2 = vpc_options.client('ec2')

            filters = [{'Name': 'vpc-id',
                        'Values': [vpc_options.vpc_id]}]

            subnets = ec2.describe_subnets(Filters=filters)
            overlapping_subnets = []
            """ iterate ips found """
            for ipfound in aws_sourceips:

                """ Iterate subnets to match ipaddress """
                for subnet in list(subnets['Subnets']):
                    ipfound = ip_network(ipfound)
                    network_addres = ip_network(subnet['CidrBlock'])

                    if ipfound.overlaps(network_addres):
                        overlapping_subnets.append("{} ({})".format(str(network_addres), subnet['SubnetId']))
            if len(overlapping_subnets) != 0:
                return "source IP(s): {} -> subnet CIDR(s): {}" \
                    .format(", ".join(aws_sourceips), ", ".join(overlapping_subnets))

        return False
