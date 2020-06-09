import importlib
import inspect
import os
from os.path import dirname
from typing import Dict, List

from shared.common import (
    ResourceProvider,
    Resource,
    message_handler,
    ResourceDigest,
    ResourceEdge,
    BaseOptions,
)
from shared.diagram import BaseDiagram
from shared.report import Report


class BaseCommand:
    def __init__(self, region_names, session, diagram):
        """
        Base class for discovery command

        :param region_names:
        :param session:
        :param diagram:
        """
        self.region_names = region_names
        self.session = session
        self.diagram = diagram


class CommandRunner(object):
    def run(
        self,
        provider: str,
        options: BaseOptions,
        diagram_builder: BaseDiagram,
        default_name: str,
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

        for provider in providers:
            provider_instance = provider[1](options)

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

        # Diagram integration
        diagram_name = diagram_builder.build(
            resources=unique_resources, resource_relations=resource_relations
        )

        # TODO: Generate reports in json/csv/pdf/xls
        report = Report()
        report.general_report(
            resources=unique_resources, resource_relations=resource_relations
        ),
        report.html_report(
            resources=unique_resources,
            resource_relations=resource_relations,
            default_name=default_name,
            diagram_name=diagram_name,
        )

        # TODO: Export in csv/json/yaml/tf... future...
        # ....exporttf(checks)....
