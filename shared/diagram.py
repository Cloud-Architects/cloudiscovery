import os
from typing import List

from shared.common import Resource
from shared.error_handler import exception

PATH_DIAGRAM_OUTPUT = "./assets/diagrams/"


class Mapsources:
    """ diagrams modules that store classes that represent diagram elements """
    diagrams_modules = ["analytics", "compute", "database", "devtools", "engagement", "integration", "iot",
                        "management", "media", "migration", "ml", "network", "security", "storage"]

    """ Class to mapping type resource from Terraform to Diagram Nodes """
    mapresources = {"aws_lambda_function": "Lambda", "aws_emr_cluster": "EMRCluster",
                    "aws_elasticsearch_domain": "ES", "aws_msk_cluster": "ManagedStreamingForKafka",
                    "aws_sqs_queue_policy": "SQS", "aws_instance": "EC2",
                    "aws_eks_cluster": "EKS", "aws_autoscaling_group": "AutoScaling",
                    "aws_ecs_cluster": "ECS", "aws_db_instance": "RDS",
                    "aws_elasticache_cluster": "ElastiCache", "aws_docdb_cluster": "DocumentDB",
                    "aws_internet_gateway": "InternetGateway", "aws_nat_gateway": "NATGateway",
                    "aws_elb_classic": "ELB", "aws_elb": "ELB",
                    "aws_route_table": "RouteTable", "aws_subnet": "PublicSubnet",
                    "aws_network_acl": "Nacl", "aws_vpc_peering_connection": "VPCPeering",
                    "aws_vpc_endpoint_gateway": "Endpoint", "aws_iam_policy": "IAM",
                    "aws_efs_file_system": "EFS", "aws_s3_bucket_policy": "S3",
                    "aws_media_connect": "ElementalMediaconnect", "aws_media_live": "ElementalMedialive"}


class BaseDiagram(object):

    def build(self, resources: List[Resource]):
        self.make_directories()
        self.generate_diagram(resources)

    @staticmethod
    def make_directories():
        """ Check if assets/diagram directory exists """
        if not os.path.isdir(PATH_DIAGRAM_OUTPUT):
            try:
                os.mkdir(PATH_DIAGRAM_OUTPUT)
            except OSError:
                print("Creation of the directory %s failed" % PATH_DIAGRAM_OUTPUT)
            else:
                print("Successfully created the directory %s " % PATH_DIAGRAM_OUTPUT)

    @exception
    def generate_diagram(self, resources: List[Resource]):
        raise NotImplementedError("Implement the diagram generation logic")


class NoDiagram(BaseDiagram):
    def generate_diagram(self, resources: List[Resource]):
        pass

    def build(self, resources: List[Resource]):
        pass
