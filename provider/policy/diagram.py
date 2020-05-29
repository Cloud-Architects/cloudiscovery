from typing import List, Dict

from diagrams import Cluster, Diagram

from shared.common import Resource, ResourceEdge, ResourceDigest
from shared.diagram import BaseDiagram, Mapsources, PATH_DIAGRAM_OUTPUT
from shared.error_handler import exception


class ProfileDiagram(BaseDiagram):

    @exception
    def generate_diagram(self, resources: List[Resource], resource_relations: List[ResourceEdge]):
        """ Importing all AWS nodes """
        for module in Mapsources.diagrams_modules:
            exec('from diagrams.aws.' + module + ' import *')

        ordered_resources = self.group_by_group(resources)

        """ Start mounting Cluster """
        nodes: Dict[ResourceDigest, any] = {}
        with Diagram(name="AWS Permissions map", filename=PATH_DIAGRAM_OUTPUT + "account_policies", direction="TB"):

            # TODO: add account
            # """ VPC to represent main resource """
            # _vpc = eval("VPC")("VPC {}".format(self.vpc_id))

            """ Iterate resources to draw it """
            for alldata in ordered_resources:
                with Cluster(alldata.capitalize() + " resources"):
                    for resource in ordered_resources[alldata]:
                        node = eval(Mapsources.mapresources.get(resource.digest.type))(resource.name)
                        nodes[resource.digest] = node

            for resource_relation in resource_relations:
                from_node = nodes[resource_relation.from_node]
                to_node = nodes[resource_relation.to_node]
                from_node >> to_node
