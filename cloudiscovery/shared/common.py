import os.path
import datetime
import re
import functools
import threading
from typing import NamedTuple, List, Optional, Dict

from diskcache import Cache

import boto3

VPCE_REGEX = re.compile(r'(?<=sourcevpce")(\s*:\s*")(vpce-[a-zA-Z0-9]+)', re.DOTALL)
SOURCE_IP_ADDRESS_REGEX = re.compile(
    r'(?<=sourceip")(\s*:\s*")([a-fA-F0-9.:/%]+)', re.DOTALL
)
FILTER_NAME_PREFIX = "Name="
FILTER_TAG_NAME_PREFIX = "tags."
FILTER_TYPE_NAME = "type"
FILTER_VALUE_PREFIX = "Value="

_LOG_SEMAPHORE = threading.Semaphore()


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


class BaseAwsOptions(NamedTuple):
    session: boto3.Session
    region_name: str

    def client(self, service_name: str):
        return self.session.client(service_name, region_name=self.region_name)

    def resulting_file_name(self, suffix):
        return "{}_{}_{}".format(self.account_number(), self.region_name, suffix)

    def account_number(self):
        client = self.session.client("sts", region_name=self.region_name)
        account_id = client.get_caller_identity()["Account"]
        return account_id


class ResourceDigest(NamedTuple):
    id: str
    type: str


class ResourceEdge(NamedTuple):
    from_node: ResourceDigest
    to_node: ResourceDigest
    label: str = None


class Filterable:
    pass


class LimitsValues(NamedTuple):
    service: str
    quota_name: str
    quota_code: str
    aws_limit: int
    local_limit: int
    usage: int
    percent: float


class ResourceTag(NamedTuple, Filterable):
    key: str
    value: str


class ResourceType(NamedTuple, Filterable):
    type: str


class Resource(NamedTuple):
    digest: ResourceDigest
    name: str = ""
    details: str = ""
    group: str = ""
    tags: List[ResourceTag] = []
    limits: List[LimitsValues] = []


class ResourceCache:
    def __init__(self):
        self.cache = Cache(
            directory=os.path.dirname(os.path.abspath(__file__))
            + "/../../assets/.cache/"
        )

    def set_key(self, key: str, value: object, expire: int):
        self.cache.set(key=key, value=value, expire=expire)

    def get_key(self, key: str):
        if key in self.cache:
            return self.cache[key]

        return None


# Decorator to check services.
class ResourceAvailable(object):
    def __init__(self, services):
        self.services = services
        self.cache = ResourceCache()

    def is_service_available(self, region_name, service_name) -> bool:
        cache_key = "aws_paths_" + region_name
        cache = self.cache.get_key(cache_key)
        return service_name in cache

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            if "vpc_options" in dir(args[0]):
                region_name = args[0].vpc_options.region_name
            elif "iot_options" in dir(args[0]):
                region_name = args[0].iot_options.region_name
            else:
                region_name = "us-east-1"

            if self.is_service_available(region_name, self.services):
                return func(*args, **kwargs)

            message_handler(
                "Check "
                + func.__qualname__
                + " not available in this region... Skipping",
                "WARNING",
            )

            return None

        return wrapper


def resource_tags(resource_data: dict) -> List[ResourceTag]:
    if "Tags" in resource_data:
        tags_input = resource_data["Tags"]
    elif "tags" in resource_data:
        tags_input = resource_data["tags"]
    elif "TagList" in resource_data:
        tags_input = resource_data["TagList"]
    elif "TagSet" in resource_data:
        tags_input = resource_data["TagSet"]
    else:
        tags_input = None

    tags = []
    if isinstance(tags_input, list):
        tags = resource_tags_from_tuples(tags_input)
    elif isinstance(tags_input, dict):
        tags = resource_tags_from_dict(tags_input)

    return tags


def resource_tags_from_tuples(tuples: List[Dict[str, str]]) -> List[ResourceTag]:
    """
        List of key-value tuples that store tags, syntax:
        [
            {
                'Key': 'string',
                'Value': 'string',
                ...
            },
        ]
        OR
        [
            {
                'key': 'string',
                'value': 'string',
                ...
            },
        ]
    """
    result = []
    for tuple_elem in tuples:
        if "Key" in tuple_elem and "Value" in tuple_elem:
            result.append(ResourceTag(key=tuple_elem["Key"], value=tuple_elem["Value"]))
        elif "key" in tuple_elem and "value" in tuple_elem:
            result.append(ResourceTag(key=tuple_elem["key"], value=tuple_elem["value"]))
    return result


def resource_tags_from_dict(tags: Dict[str, str]) -> List[ResourceTag]:
    """
        List of key-value dict that store tags, syntax:
        {
            'string': 'string'
        }
    """
    result = []
    for key, value in tags.items():
        result.append(ResourceTag(key=key, value=value))
    return result


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


def get_name_tag(d) -> Optional[str]:
    return get_tag(d, "Name")


def get_tag(d, tag_name) -> Optional[str]:
    for k, v in d.items():
        if k in ("Tags", "TagList"):
            for value in v:
                if value["Key"] == tag_name:
                    return value["Value"]

    return None


def generate_session(profile_name):
    try:
        return boto3.Session(profile_name=profile_name)
    # pylint: disable=broad-except
    except Exception as e:
        message = "You must configure awscli before use this script.\nError: {0}".format(
            str(e)
        )
        exit_critical(message)


def exit_critical(message):
    log_critical(message)
    raise SystemExit


def log_critical(message):
    message_handler(message, "FAIL")


def message_handler(message, position):
    _LOG_SEMAPHORE.acquire()
    print(bcolors.colors.get(position), message, bcolors.colors.get("ENDC"), sep="")
    _LOG_SEMAPHORE.release()


# pylint: disable=inconsistent-return-statements
def datetime_to_string(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()


def _add_filter(filters: List[Filterable], is_tag: bool, full_name: str, value: str):
    if is_tag:
        name = full_name[len(FILTER_TAG_NAME_PREFIX) :]
        filters.append(ResourceTag(key=name, value=value))
    else:
        filters.append(ResourceType(type=value))


def parse_filters(arg_filters) -> List[Filterable]:
    filters: List[Filterable] = []
    for arg_filter in arg_filters:
        filter_parts = arg_filter.split(";")
        if len(filter_parts) != 2:
            continue
        if not filter_parts[0].startswith(FILTER_NAME_PREFIX):
            continue
        if not filter_parts[1].startswith(FILTER_VALUE_PREFIX):
            continue
        full_name = filter_parts[0][len(FILTER_NAME_PREFIX) :]
        is_tag = False
        if full_name.startswith(FILTER_TAG_NAME_PREFIX):
            is_tag = True
        elif full_name != FILTER_TYPE_NAME:
            continue
        values = filter_parts[1][len(FILTER_VALUE_PREFIX) :]

        val_buffered = True
        wrapped = False
        val_buffer = []
        for character in values:
            # pylint: disable=no-else-continue
            if character == "'":
                wrapped = not wrapped
                continue
            # pylint: disable=no-else-continue
            elif character == ":":
                if len(val_buffer) == 0:
                    continue
                elif val_buffered and not wrapped:
                    _add_filter(filters, is_tag, full_name, "".join(val_buffer))
                    val_buffered = False
                    val_buffer = []
                    continue
            val_buffered = True
            val_buffer.append(character)
        if len(val_buffer) > 0:
            _add_filter(filters, is_tag, full_name, "".join(val_buffer))

    return filters


def get_paginator(client, operation_name, resource_type):
    """
    TODO: Possible circular reference using in common_aws, move to there in future.
    """
    # Checking if can page
    if client.can_paginate(operation_name):
        paginator = client.get_paginator(operation_name)
        if resource_type == "aws_iam_policy":
            pages = paginator.paginate(
                Scope="Local"
            )  # hack to list only local IAM policies - aws_all
        else:
            pages = paginator.paginate()
    else:
        return False

    return pages
