import importlib
import inspect
import os
from os.path import dirname
from typing import Dict, List

from boto3 import Session

from shared.common import (
    ResourceProvider,
    Resource,
    message_handler,
    ResourceDigest,
    ResourceEdge,
    BaseAwsOptions,
    Filterable,
    ResourceTag,
    ResourceType,
)
from shared.diagram import BaseDiagram
from shared.report import Report


class BaseCommand:
    def __init__(self, region_names, session, diagram, filters):
        """
        Base class for discovery command

        :param region_names:
        :param session:
        :param diagram:
        :param filters:
        """
        self.region_names: List[str] = region_names
        self.session: Session = session
        self.diagram: bool = diagram
        self.filters: List[Filterable] = filters


def filter_resources(
    resources: List[Resource], filters: List[Filterable]
) -> List[Resource]:
    if len(filters) == 0:
        return resources

    filtered_resources = []
    for resource in resources:
        matches_filter = False
        for resource_filter in filters:
            if isinstance(resource_filter, ResourceTag):
                for resource_tag in resource.tags:
                    if (
                        resource_tag.key == resource_filter.key
                        and resource_tag.value == resource_filter.value
                    ):
                        matches_filter = True
            elif isinstance(resource_filter, ResourceType):
                if resource.digest.type == resource_filter.type:
                    matches_filter = True
        if matches_filter:
            filtered_resources.append(resource)
    return filtered_resources


def filter_relations(
    filtered_resources: List[Resource], resource_relations: List[ResourceEdge]
):
    filtered_relations: List[ResourceEdge] = []

    for resource_relation in resource_relations:
        is_from_present = False
        is_to_present = False
        for resource in filtered_resources:
            if resource_relation.from_node == resource.digest:
                is_from_present = True
            if resource_relation.to_node == resource.digest:
                is_to_present = True
        if is_from_present and is_to_present:
            filtered_relations.append(resource_relation)
    return filtered_relations


class CommandRunner(object):
    def __init__(self, filters):
        """
        Base class command execution

        :param filters:
        """
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

        for providerTuple in providers:
            provider_instance = providerTuple[1](options)

            provider_resources = provider_instance.get_resources()
            if provider_resources is not None:
                all_resources.extend(provider_resources)

            provider_resource_relations = provider_instance.get_relations()
            if provider_resource_relations is not None:
                resource_relations.extend(provider_resource_relations)

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
