from typing import List, Dict, Optional


from cachetools import TTLCache

from shared.command import CommandRunner
from shared.common import (
    ResourceCache,
    Filterable,
    BaseCommand,
)
from ibm_vpc import VpcV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_cloud_sdk_core import ApiException

SUBNET_CACHE = TTLCache(maxsize=1024, ttl=60)


def describe_subnet(service, subnet_ids):
    if not isinstance(subnet_ids, list):
        subnet_ids = [subnet_ids]

    if str(subnet_ids) in SUBNET_CACHE:
        return SUBNET_CACHE[str(subnet_ids)]

    try:
        subnets = service.list_subnets()
        SUBNET_CACHE[str(subnet_ids)] = subnets
        return subnets
    except ApiException as e:
        print("List Subnets failed with status code " + str(e.code) + ": " + e.message)


class BaseIbmOptions:
    region: str
    apikey: str
    service: VpcV1

    def __init__(self, apikey, region):
        """
        Base IBM options

        :param session:
        :param region_name:
        """
        self.region = region
        self.apikey = apikey
        authenticator = IAMAuthenticator(self.apikey)
        self.service = VpcV1(authenticator=authenticator)
        vpc_url = "https://" + region + ".iaas.cloud.ibm.com"
        self.service.set_service_url(vpc_url)
        self.service = VpcV1("2020-04-10", authenticator=authenticator)

    def client(self):
        return self.service


class GlobalParameters:
    def __init__(self, apikey, region: str):
        self.region = region
        self.apikey = apikey
        authenticator = IAMAuthenticator(self.apikey)
        self.service = VpcV1(authenticator=authenticator)
        vpc_url = "https://" + region + ".iaas.cloud.ibm.com"
        self.service.set_service_url(vpc_url)
        self.service = VpcV1("2020-04-10", authenticator=authenticator)
        self.cache = ResourceCache()


class BaseIbmCommand(BaseCommand):
    region: str
    apikey: str
    url: str
    service: VpcV1

    def __init__(self, region, apikey, url):
        """
        Base class for discovery command

        :param region:
        :param apikey:
        """
        self.region = region
        self.apikey = apikey
        authenticator = IAMAuthenticator(self.apikey)
        self.service = VpcV1(authenticator=authenticator)
        vpc_url = url
        self.service.set_service_url(vpc_url)
        self.service = VpcV1("2020-04-10", authenticator=authenticator)

    # pylint: disable=too-many-arguments
    def run(
        self,
        diagram: bool,
        verbose: bool,
        services: List[str],
        filters: List[Filterable],
        import_module: str,
    ):
        raise NotImplementedError()


def resource_tags(resource_data: dict) -> List[Filterable]:
    if isinstance(resource_data, str):
        return []

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


def resource_tags_from_tuples(tuples: List[Dict[str, str]]) -> List[Filterable]:
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
            result.append(Filterable(key=tuple_elem["Key"], value=tuple_elem["Value"]))
        elif "key" in tuple_elem and "value" in tuple_elem:
            result.append(Filterable(key=tuple_elem["key"], value=tuple_elem["value"]))
    return result


def resource_tags_from_dict(tags: Dict[str, str]) -> List[Filterable]:
    """
    List of key-value dict that store tags, syntax:
    {
        'string': 'string'
    }
    """
    result = []
    for key, value in tags.items():
        result.append(Filterable(key=key, value=value))
    return result


# pylint: disable=unsubscriptable-object
def get_name_tag(d) -> Optional[str]:
    return get_tag(d, "Name")


# pylint: disable=unsubscriptable-object
def get_tag(d, tag_name) -> Optional[str]:
    for k, v in d.items():
        if k in ("Tags", "TagList"):
            for value in v:
                if value["Key"] == tag_name:
                    return value["Value"]

    return None


def get_paginator(client, operation_name, resource_type, filters=None):
    # Checking if can paginate
    if client.can_paginate(operation_name):
        paginator = client.get_paginator(operation_name)
        if resource_type == "aws_iam_policy":
            pages = paginator.paginate(
                Scope="Local"
            )  # hack to list only local IAM policies - aws_all
        else:
            if filters:
                pages = paginator.paginate(**filters)
            else:
                pages = paginator.paginate()
    else:
        return False

    return pages


class IbmCommandRunner(CommandRunner):
    def __init__(self, filters: List[Filterable] = None):
        """
        IBM command execution

        :param filters:
        """
        super().__init__("ibm", filters)
