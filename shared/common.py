from typing import NamedTuple
import datetime
import boto3
import re
from ipaddress import ip_network, ip_address

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


def generate_session(profile_name):
    try:
        return boto3.Session(profile_name=profile_name)
    except Exception as e:
        message = "You must configure awscli before use this script.\nError: {0}".format(str(e))
        exit_critical(message)


def exit_critical(message):
    print(bcolors.colors.get('FAIL'), message, bcolors.colors.get('ENDC'), sep="")
    raise SystemExit


def message_handler(message, position):
    print(bcolors.colors.get(position), message, bcolors.colors.get('ENDC'), sep="")


def datetime_to_string(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

def check_ipvpc_inpolicy(document, vpc_options: VpcOptions):
    
    """ Replace json slashes """
    document = document.replace("\\","")

    """ Checking if VPC is inside document, it's a 100% true information """
    if vpc_options.vpc_id in document:
        return True, "No-subnet"
    else:
        """ 
        Vpc_id not found, trying to discover if it's a potencial subnet IP 
        TODO: improve this check
        TODO: improve regexp
        """
        try:
            if "aws:SourceIp" in document:

                """ Get ip found """
                aws_sourceip = re.findall(r'(?<=SourceIp")(?:\s*\:\s*)("?.{0,500}(?=")")', document, re.DOTALL)[0]
                """ Piece of shit code """
                aws_sourceip = aws_sourceip.replace('"','').replace("[","") \
                                                           .replace("{","") \
                                                           .replace("]","") \
                                                           .replace("}","") \
                                                           .split(",")

                """ Get subnets cidr block """ 
                ec2 = vpc_options.session.resource('ec2', region_name=vpc_options.region_name)
                
                filters = [{'Name':'vpc-id', 
                            'Values':[vpc_options.vpc_id]}]
                
                subnets = ec2.subnets.filter(Filters=filters)

                """ iterate ips found """
                for ipfound in aws_sourceip:

                    """ Iterate subnets to match ipaddress """
                    for subnet in list(subnets):

                        ipfound = ip_network(ipfound)
                        network_addres = ip_network(subnet.cidr_block)

                        if ipfound.overlaps(network_addres):
                            return True, "Subnet: {0} - CIDR - {1}".format(str(subnet.subnet_id), str(subnet.cidr_block))

        except:
            return False, "No-subnet"

        return False, "No-subnet"
