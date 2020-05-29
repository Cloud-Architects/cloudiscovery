from typing import List

from diagrams import Cluster, Diagram

from shared.common import Resource
from shared.diagram import BaseDiagram, Mapsources, PATH_DIAGRAM_OUTPUT
from shared.error_handler import exception


class ProfileDiagram(BaseDiagram):

    @exception
    def generate_diagram(self, resources: List[Resource]):
        """ Importing all AWS nodes """
        for module in Mapsources.diagrams_modules:
            exec('from diagrams.aws.' + module + ' import *')

        """ Ordering Resource list to group resources into cluster """
        ordered_resources = dict()
        for rundata in resources:
            if Mapsources.mapresources.get(rundata.type) is not None:
                if rundata.group in ordered_resources:
                    ordered_resources[rundata.group].append({"id": rundata.id,
                                                             "type": rundata.type,
                                                             "name": rundata.name,
                                                             "details": rundata.details})
                else:
                    ordered_resources[rundata.group] = [{"id": rundata.id,
                                                         "type": rundata.type,
                                                         "name": rundata.name,
                                                         "details": rundata.details}]

        """ Start mounting Cluster """
        resource_id = list()
        with Diagram(name="AWS Permissions map", filename=PATH_DIAGRAM_OUTPUT + "account_policies", direction="TB"):

            # TODO: add account
            # """ VPC to represent main resource """
            # _vpc = eval("VPC")("VPC {}".format(self.vpc_id))

            """ Iterate resources to draw it """
            for alldata in ordered_resources:
                with Cluster(alldata.capitalize() + " resources"):
                    for rundata in ordered_resources[alldata]:
                        resource_id.append(eval(Mapsources.mapresources.get(rundata["type"]))(rundata["name"]))

            # """ Connecting resources and vpc """
            # for resource in resource_id:
            #     resource >> _vpc
