import importlib
import inspect
import os
from concurrent.futures.thread import ThreadPoolExecutor
from os.path import dirname
from typing import List, Dict, Optional

import botocore.exceptions
import boto3
from boto3 import Session
from cachetools import TTLCache

from shared.command import execute_provider, filter_resources, filter_relations
from shared.common import (
    ResourceCache,
    message_handler,
    ResourceTag,
    ResourceProvider,
    Resource,
    ResourceEdge,
    ResourceDigest,
    Filterable,
    exit_critical,
    BaseCommand,
)
from shared.diagram import BaseDiagram
from shared.report import Report

SUBNET_CACHE = TTLCache(maxsize=1024, ttl=60)


def describe_subnet(vpc_options, subnet_ids):
    if not isinstance(subnet_ids, list):
        subnet_ids = [subnet_ids]

    if str(subnet_ids) in SUBNET_CACHE:
        return SUBNET_CACHE[str(subnet_ids)]

    ec2 = vpc_options.client("ec2")
    try:
        subnets = ec2.describe_subnets(SubnetIds=subnet_ids)
        SUBNET_CACHE[str(subnet_ids)] = subnets
        return subnets
    except botocore.exceptions.ClientError:
        return None


def aws_verbose():
    """
    Boto3 only provides usable information in DEBUG mode
    Using empty name it catchs debug from boto3/botocore
    TODO: Open a ticket in boto3/botocore project to provide more information at other levels of debugging
    """
    boto3.set_stream_logger(name="")


class BaseAwsOptions:
    session: boto3.Session
    region_name: str

    def __init__(self, session, region_name):
        """
        Base AWS options

        :param session:
        :param region_name:
        """
        self.session = session
        self.region_name = region_name

    def client(self, service_name: str):
        return self.session.client(service_name, region_name=self.region_name)

    def resulting_file_name(self, suffix):
        return "{}_{}_{}".format(self.account_number(), self.region_name, suffix)

    def account_number(self):
        client = self.session.client("sts", region_name=self.region_name)
        account_id = client.get_caller_identity()["Account"]
        return account_id


class GlobalParameters:
    def __init__(self, session, region: str, path: str):
        self.region = region
        self.session = session.client("ssm", region_name="us-east-1")
        self.path = path
        self.cache = ResourceCache()

    def get_parameters_by_path(self, next_token=None):

        params = {"Path": self.path, "Recursive": True, "MaxResults": 10}
        if next_token is not None:
            params["NextToken"] = next_token

        return self.session.get_parameters_by_path(**params)

    def parameters(self):
        next_token = None
        while True:
            response = self.get_parameters_by_path(next_token)
            parameters = response["Parameters"]
            if not parameters:
                break
            for parameter in parameters:
                yield parameter
            if "NextToken" not in response:
                break
            next_token = response["NextToken"]

    def paths(self):

        cache_key = "aws_paths_" + self.region
        cache = self.cache.get_key(cache_key)

        if cache is not None:
            return cache

        message_handler(
            "Fetching available resources in region {} to cache...".format(self.region),
            "HEADER",
        )
        paths_found = []
        paths = self.parameters()
        for path in paths:
            paths_found.append(path["Value"])

        self.cache.set_key(key=cache_key, value=paths_found, expire=86400)
        return paths_found


class BaseAwsCommand(BaseCommand):
    def __init__(self, region_names, session):
        """
        Base class for discovery command

        :param region_names:
        :param session:
        """
        self.region_names: List[str] = region_names
        self.session: Session = session

    def run(
        self,
        diagram: bool,
        verbose: bool,
        services: List[str],
        filters: List[Filterable],
    ):
        raise NotImplementedError()

    def init_region_cache(self, region):
        # Get and cache SSM services available in specific region
        path = "/aws/service/global-infrastructure/regions/" + region + "/services/"
        GlobalParameters(session=self.session, region=region, path=path).paths()


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


def get_name_tag(d) -> Optional[str]:
    return get_tag(d, "Name")


def get_tag(d, tag_name) -> Optional[str]:
    for k, v in d.items():
        if k in ("Tags", "TagList"):
            for value in v:
                if value["Key"] == tag_name:
                    return value["Value"]

    return None


def generate_session(profile_name, region_name):
    try:
        return boto3.Session(profile_name=profile_name, region_name=region_name)
    # pylint: disable=broad-except
    except Exception as e:
        message = "You must configure awscli before use this script.\nError: {0}".format(
            str(e)
        )
        exit_critical(message)


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


class AwsCommandRunner(object):
    def __init__(self, services=None, filters=None):
        """
        Base class command execution

        :param services:
        :param filters:
        """
        self.services: List[str] = services
        self.filters: List[Filterable] = filters

    # pylint: disable=too-many-locals,too-many-arguments
    def run(
        self,
        provider: str,
        options: BaseAwsOptions,
        diagram_builder: BaseDiagram,
        title: str,
        filename: str,
    ):
        """
        Executes a command.

        The project's development pattern is a file with the respective name of the parent
        resource (e.g. compute, network), classes of child resources inside this file and run() method to execute
        respective check. So it makes sense to load dynamically.
        """
        # Iterate to get all modules
        message_handler("\nInspecting resources", "HEADER")
        providers = []
        for name in os.listdir(
            dirname(__file__) + "/../provider/" + provider + "/resource"
        ):
            if name.endswith(".py"):
                # strip the extension
                module = name[:-3]

                # Load and call all run check
                for nameclass, cls in inspect.getmembers(
                    importlib.import_module(
                        "provider." + provider + ".resource." + module
                    ),
                    inspect.isclass,
                ):
                    if (
                        issubclass(cls, ResourceProvider)
                        and cls is not ResourceProvider
                    ):
                        providers.append((nameclass, cls))
        providers.sort(key=lambda x: x[0])

        all_resources: List[Resource] = []
        resource_relations: List[ResourceEdge] = []

        with ThreadPoolExecutor(15) as executor:
            provider_results = executor.map(
                lambda data: execute_provider(options, data), providers
            )

        for provider_results in provider_results:
            if provider_results[0] is not None:
                all_resources.extend(provider_results[0])
            if provider_results[1] is not None:
                resource_relations.extend(provider_results[1])

        unique_resources_dict: Dict[ResourceDigest, Resource] = dict()
        for resource in all_resources:
            unique_resources_dict[resource.digest] = resource

        unique_resources = list(unique_resources_dict.values())

        unique_resources.sort(key=lambda x: x.group + x.digest.type + x.name)
        resource_relations.sort(
            key=lambda x: x.from_node.type
            + x.from_node.id
            + x.to_node.type
            + x.to_node.id
        )

        # Resource filtering and sorting
        filtered_resources = filter_resources(unique_resources, self.filters)
        filtered_resources.sort(key=lambda x: x.group + x.digest.type + x.name)

        # Relationships filtering and sorting
        filtered_relations = filter_relations(filtered_resources, resource_relations)
        filtered_relations.sort(
            key=lambda x: x.from_node.type
            + x.from_node.id
            + x.to_node.type
            + x.to_node.id
        )

        # Diagram integration
        diagram_builder.build(
            resources=filtered_resources,
            resource_relations=filtered_relations,
            title=title,
            filename=filename,
        )

        # TODO: Generate reports in json/csv/pdf/xls
        report = Report()
        report.general_report(
            resources=filtered_resources, resource_relations=filtered_relations
        ),
        report.html_report(
            resources=filtered_resources,
            resource_relations=filtered_relations,
            title=title,
            filename=filename,
        )

        # TODO: Export in csv/json/yaml/tf... future...
        # ....exporttf(checks)....
