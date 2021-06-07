import importlib
import inspect
from concurrent.futures.thread import ThreadPoolExecutor
from os.path import dirname
from typing import List, Dict
import os

from shared.common import (
    Resource,
    ResourceEdge,
    Filterable,
    BaseOptions,
    message_handler,
    ResourceProvider,
    ResourceDigest,
)
from shared.diagram import BaseDiagram
from shared.report import Report


class CommandRunner(object):
    def __init__(self, provider_name: str, filters: List[Filterable] = None):
        """
        Base class command execution

        :param provider_name:
        :param filters:
        """
        self.provider_name: str = provider_name
        self.filters: List[Filterable] = filters

    # pylint: disable=too-many-locals,too-many-arguments
    def run(
        self,
        provider: str,
        options: BaseOptions,
        diagram_builder: BaseDiagram,
        title: str,
        filename: str,
        import_module: str,
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
            dirname(__file__)
            + "/../provider/"
            + self.provider_name
            + "/"
            + provider
            + "/resource"
        ):
            if name.endswith(".py"):
                # strip the extension
                module = name[:-3]

                # Load and call all run check
                for nameclass, cls in inspect.getmembers(
                    importlib.import_module(
                        import_module
                        #"provider.aws."
                        + provider.replace("/", ".")
                        + ".resource."
                        + module
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

            for provider_result in provider_results:
                if provider_result[0] is not None:
                    all_resources.extend(provider_result[0])
                if provider_result[1] is not None:
                    resource_relations.extend(provider_result[1])
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
        )
        report.html_report(
            resources=filtered_resources,
            resource_relations=filtered_relations,
            title=title,
            filename=filename,
        )

        # TODO: Export in csv/json/yaml/tf... future...
        # ....exporttf(checks)....


def execute_provider(options, data) -> (List[Resource], List[ResourceEdge]):
    provider_instance = data[1](options)
    provider_resources = provider_instance.get_resources()
    provider_resource_relations = provider_instance.get_relations()
    return provider_resources, provider_resource_relations


def filter_resources(
    resources: List[Resource], filters: List[Filterable]
) -> List[Resource]:
    if not filters:
        return resources

    filtered_resources = []
    for resource in resources:
        matches_filter = False
        for resource_filter in filters:
            if resource_filter.is_tag():
                for resource_tag in resource.tags:
                    if (
                        resource_tag.key == resource_filter.key
                        and resource_tag.value == resource_filter.value
                    ):
                        matches_filter = True
            elif resource_filter.is_type():
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
