import os
from typing import List, Dict

from shared.common import Resource, ResourceEdge
from shared.error_handler import exception

PATH_DIAGRAM_OUTPUT = "./assets/diagrams/"


class Mapsources:
    """ diagrams modules that store classes that represent diagram elements """
    diagrams_modules = ["analytics", "compute", "database", "devtools", "engagement", "game", "general", "integration",
                        "iot", "management", "media", "migration", "ml", "network", "robotics", "security", "storage"]

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
                    "aws_vpc_endpoint_gateway": "Endpoint", "aws_iam_policy": "IAM", "aws_iam_user": "User",
                    "aws_iam_group": "IAM", "aws_efs_file_system": "EFS", "aws_s3_bucket_policy": "S3",
                    "aws_media_connect": "ElementalMediaconnect", "aws_media_live": "ElementalMedialive"}


class BaseDiagram(object):

    def build(self, resources: List[Resource], resource_relations: List[ResourceEdge]):
        self.make_directories()
        self.generate_diagram(resources, resource_relations)

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

    @staticmethod
    def group_by_group(resources):
        """ Ordering Resource list to group resources into cluster """
        ordered_resources: Dict[str, List[Resource]] = dict()
        for resource in resources:
            if Mapsources.mapresources.get(resource.digest.type) is not None:
                if resource.group in ordered_resources:
                    ordered_resources[resource.group].append(resource)
                else:
                    ordered_resources[resource.group] = [resource]
        return ordered_resources

    @exception
    def generate_diagram(self, resources: List[Resource], resource_relations: List[ResourceEdge]):
        raise NotImplementedError("Implement the diagram generation logic")


class NoDiagram(BaseDiagram):
    def generate_diagram(self, resources: List[Resource], resource_relations: List[ResourceEdge]):
        pass

    def build(self, resources: List[Resource], resource_relations: List[ResourceEdge]):
        pass
