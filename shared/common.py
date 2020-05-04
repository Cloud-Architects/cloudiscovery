from typing import NamedTuple
import datetime
import boto3


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
