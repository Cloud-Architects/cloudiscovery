import importlib
import inspect
import os

from shared.diagram import BaseDiagram
from shared.report import Report
from shared.common import *


class BaseCommand:
    def __init__(self, region_name, session, diagram):
        self.region_name = region_name
        self.session = session
        self.diagram = diagram

    def check_region(self):
        client = self.session.client('ec2')

        regions = [region['RegionName'] for region in client.describe_regions()['Regions']]

        if self.region_name not in regions:
            message = "There is no region named: {0}".format(self.region_name)
            exit_critical(message)


class CommandRunner(object):

    def run(self, provider: str, options: BaseOptions, diagram_builder: BaseDiagram):
        """
        The project's development pattern is a file with the respective name of the parent
        resource (e.g. compute, network), classes of child resources inside this file and run() method to execute
        respective check. So it makes sense to load dynamically.
        """

        """ Iterate to get all modules """
        message_handler("\nInspecting resources", "HEADER")
        providers = []
        for name in os.listdir("provider/" + provider + "/resource"):
            if name.endswith(".py"):
                # strip the extension
                module = name[:-3]

                """ Load and call all run check """
                for nameclass, cls in inspect.getmembers(
                        importlib.import_module("provider." + provider + ".resource." + module), inspect.isclass):
                    if issubclass(cls, ResourceProvider) and cls is not ResourceProvider:
                        providers.append((nameclass, cls))
        providers.sort(key=lambda x: x[0])

        resources: List[Resource] = []
        resource_relations: List[ResourceEdge] = []

        for provider in providers:
            provider_instance = provider[1](options)

            provider_resources = provider_instance.get_resources()
            if provider_resources is not None:
                resources.extend(provider_resources)

            provider_resource_relations = provider_instance.get_relations()
            if provider_resource_relations is not None:
                resource_relations.extend(provider_resource_relations)

        resources.sort(key=lambda x: x.group + x.digest.type + x.name)
        resource_relations.sort(key=lambda x: x.from_node.type + x.from_node.id + x.to_node.type + x.to_node.id)

        """ 
        TODO: Generate reports in json/csv/pdf/xls 
        """
        Report().general_report(resources=resources, resource_relations=resource_relations)

        """ 
        Diagram integration
        """
        diagram_builder.build(resources=resources, resource_relations=resource_relations)

        """
        TODO: Export in csv/json/yaml/tf... future...
        """
        # ....exporttf(checks)....
