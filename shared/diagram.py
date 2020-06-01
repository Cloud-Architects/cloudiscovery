import os
from typing import List, Dict

from diagrams import Diagram, Cluster, Edge

from shared.common import Resource, ResourceEdge, ResourceDigest
from shared.error_handler import exception

PATH_DIAGRAM_OUTPUT = "./assets/diagrams/"


class Mapsources:
    """ diagrams modules that store classes that represent diagram elements """
    diagrams_modules = ["analytics", "compute", "database", "devtools", "engagement", "game", "general", "integration",
                        "iot", "management", "media", "migration", "ml", "network", "robotics", "security", "storage"]

    """ Class to mapping type resource from Terraform to Diagram Nodes """
    mapresources = {"aws_lambda_function": "Lambda", "aws_emr_cluster": "EMRCluster", "aws_emr": "EMR",
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
                    "aws_iam_group": "IAM", "aws_iam_role": "IAMRole", "aws_iam_instance_profile": "IAM",
                    "aws_efs_file_system": "EFS", "aws_s3_bucket_policy": "S3",
                    "aws_media_connect": "ElementalMediaconnect", "aws_media_live": "ElementalMedialive",
                    "aws_api_gateway_rest_api": "APIGateway", "aws_sagemaker_notebook_instance": "Sagemaker",
                    "aws_ssm_document": "SSM", "aws_cognito_identity_provider": "Cognito",
                    "aws_iot_thing": "InternetOfThings", "aws_general": "General", "aws_appsync_graphql_api": "Appsync",
                    "aws_iot_analytics": "IotAnalytics", "aws_securityhub_account": "SecurityHub",
                    "aws_trusted_advisor": "TrustedAdvisor", "aws_kinesis_firehose": "KinesisDataFirehose",
                    "aws_glue": "Glue", "aws_quicksight": "Quicksight", "aws_cloud9": "Cloud9",
                    "aws_organizations_account": "Organizations", "aws_config": "Config",
                    "aws_auto_scaling": "AutoScaling", "aws_backup": "Backup", "aws_cloudtrail": "Cloudtrail",
                    "aws_cloudwatch": "Cloudwatch", "aws_data_pipeline": "DataPipeline", "aws_dms": "DMS",
                    "aws_elastic_beanstalk_environment": "EB", "aws_fms": "FMS", "aws_global_accelerator": "GAX",
                    "aws_inspector": "Inspector", "aws_cloudfront_distribution": "CloudFront",
                    "aws_migration_hub": "MigrationHub", "aws_sns_topic": "SNS"}


class BaseDiagram(object):
    def __init__(self, name: str, filename: str):
        self.name = name
        self.filename = filename

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
        """ Importing all AWS nodes """
        for module in Mapsources.diagrams_modules:
            exec('from diagrams.aws.' + module + ' import *')

        ordered_resources = self.group_by_group(resources)

        """ Start mounting Cluster """
        nodes: Dict[ResourceDigest, any] = {}
        with Diagram(name=self.name, filename=PATH_DIAGRAM_OUTPUT + self.filename, direction="TB",
                     graph_attr={
                         "nodesep": "2.0",
                         "ranksep": "1.0",
                         "splines": "curved",
                     }) as d:
            d.dot.engine = 'sfdp'

            """ Iterate resources to draw it """
            for alldata in ordered_resources:
                if alldata == '':
                    for resource in ordered_resources[alldata]:
                        node = eval(Mapsources.mapresources.get(resource.digest.type))(resource.name)
                        nodes[resource.digest] = node
                else:
                    with Cluster(alldata.capitalize() + " resources"):
                        for resource in ordered_resources[alldata]:
                            node = eval(Mapsources.mapresources.get(resource.digest.type))(resource.name)
                            nodes[resource.digest] = node

            for resource_relation in resource_relations:
                if resource_relation.from_node in nodes and resource_relation.to_node in nodes:
                    from_node = nodes[resource_relation.from_node]
                    to_node = nodes[resource_relation.to_node]
                    from_node >> Edge(label=resource_relation.label) >> to_node

            self.customize_diagram(nodes)

    def customize_diagram(self, nodes: Dict[ResourceDigest, any]):
        pass


class NoDiagram(BaseDiagram):
    def __init__(self):
        super().__init__('', '')

    def generate_diagram(self, resources: List[Resource], resource_relations: List[ResourceEdge]):
        pass

    def build(self, resources: List[Resource], resource_relations: List[ResourceEdge]):
        pass
