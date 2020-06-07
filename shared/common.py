import datetime
import re
from typing import NamedTuple, List

import boto3

VPCE_REGEX = re.compile(r'(?<=sourcevpce")(\s*:\s*")(vpce-[a-zA-Z0-9]+)', re.DOTALL)
SOURCE_IP_ADDRESS_REGEX = re.compile(
    r'(?<=sourceip")(\s*:\s*")([a-fA-F0-9.:/%]+)', re.DOTALL
)


class bcolors:
    colors = {
        "HEADER": "\033[95m",
        "OKBLUE": "\033[94m",
        "OKGREEN": "\033[92m",
        "WARNING": "\033[93m",
        "FAIL": "\033[91m",
        "ENDC": "\033[0m",
        "BOLD": "\033[1m",
        "UNDERLINE": "\033[4m",
    }


class BaseOptions(NamedTuple):
    session: boto3.Session
    region_name: str

    def client(self, service_name: str):
        return self.session.client(service_name, region_name=self.region_name)


class ResourceDigest(NamedTuple):
    id: str
    type: str


class ResourceEdge(NamedTuple):
    from_node: ResourceDigest
    to_node: ResourceDigest
    label: str = None


class Resource(NamedTuple):
    digest: ResourceDigest
    name: str
    details: str = ""
    group: str = ""


class ResourceProvider:
    def __init__(self):
        """
        Base provider class that provides resources and relationships.

        The class should be implemented to return resources of the same type
        """
        self.relations_found: List[ResourceEdge] = []

    def get_resources(self) -> List[Resource]:
        return []

    def get_relations(self) -> List[ResourceEdge]:
        return self.relations_found


def get_name_tags(d):
    for k, v in d.items():
        if isinstance(v, dict):
            get_name_tags(v)
        else:
            if k == "Tags":
                for value in v:
                    if value["Key"] == "Name":
                        return value["Value"]

    return False


def generate_session(profile_name):
    try:
        return boto3.Session(profile_name=profile_name)
    except Exception as e:
        message = "You must configure awscli before use this script.\nError: {0}".format(
            str(e)
        )
        exit_critical(message)


def exit_critical(message):
    log_critical(message)
    raise SystemExit


def log_critical(message):
    print(bcolors.colors.get("FAIL"), message, bcolors.colors.get("ENDC"), sep="")


def message_handler(message, position):
    print(bcolors.colors.get(position), message, bcolors.colors.get("ENDC"), sep="")


def datetime_to_string(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()
