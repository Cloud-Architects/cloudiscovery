from typing import Dict

from diagrams.aws.network import VPC

from shared.common import ResourceDigest
from shared.diagram import BaseDiagram


class VpcDiagram(BaseDiagram):
    def __init__(self, vpc_id):
        self.vpc_id = vpc_id

    def customize_diagram(self, nodes: Dict[ResourceDigest, any]):
        vpc = VPC("VPC {}".format(self.vpc_id))
        for resource in nodes.values():
            resource >> vpc
