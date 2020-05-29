from typing import List

from diagrams import Cluster, Diagram

from shared.common import Resource, ResourceEdge
from shared.diagram import BaseDiagram, Mapsources, PATH_DIAGRAM_OUTPUT
from shared.error_handler import exception


class VpcDiagram(BaseDiagram):

    def __init__(self, vpc_id):
        self.vpc_id = vpc_id

    @exception
    def generate_diagram(self, resources: List[Resource], resource_relations: List[ResourceEdge]):
        """ Importing all AWS nodes """
        for module in Mapsources.diagrams_modules:
            exec('from diagrams.aws.'+module+' import *')

        ordered_resources = self.group_by_group(resources)

        """ Start mounting Cluster """
        nodes = list()
        with Diagram(name="AWS VPC {} Resources".format(self.vpc_id), filename=PATH_DIAGRAM_OUTPUT + self.vpc_id,
                     direction="TB"):

            """ VPC to represent main resource """
            _vpc = eval("VPC")("VPC {}".format(self.vpc_id))

            for alldata in ordered_resources:
                with Cluster(alldata.capitalize() + " resources"):
                    for resource in ordered_resources[alldata]:
                        node = eval(Mapsources.mapresources.get(resource.digest.type))(resource.name)
                        nodes.append(node)

            """ Connecting resources and vpc """
            for resource in nodes:
                resource >> _vpc
