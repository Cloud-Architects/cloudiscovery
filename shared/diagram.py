from shared.common import *
from shared.error_handler import exception
import os
from diagrams import Cluster, Diagram
""" Importing all AWS nodes """
from diagrams.aws.analytics import *
from diagrams.aws.compute import *
from diagrams.aws.database import *
from diagrams.aws.devtools import *
from diagrams.aws.engagement import *
from diagrams.aws.integration import *
from diagrams.aws.iot import *
from diagrams.aws.management import *
from diagrams.aws.media import *
from diagrams.aws.migration import *
from diagrams.aws.ml import *
from diagrams.aws.network import *
from diagrams.aws.security import *
from diagrams.aws.storage import *


PATH_DIAGRAM_OUTPUT = "./assets/diagrams/"

class Mapsources:

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
                    "aws_efs_file_system": "EFS", "aws_s3_bucket_policy": "S3"}


class _Diagram(object):

    def __init__ (self, vpc_id, diagram, resources):
        self.resources = resources
        self.vpc_id = vpc_id
        self.diagram = diagram

    @exception
    def generateDiagram(self):
       
        #diagram = [[], [], [], [], [], [], [Resource(id='j-HCK3AB8SJ0JK', name='My cluster', type='aws_emr_cluster', details='', group='compute'), Resource(id='j-UU8T5E0AI99S', name='My cluster', type='aws_emr_cluster', details='', group='compute')], [Resource(id='arn:aws:lambda:us-east-1:200984112386:function:cwsyn-meucana-2b5c2c74-cbfc-46b5-8400-db853e98dca3', name='cwsyn-meucana-2b5c2c74-cbfc-46b5-8400-db853e98dca3', type='aws_lambda_function', details='', group='compute'), Resource(id='arn:aws:lambda:us-east-1:200984112386:function:myfnn', name='myfnn', type='aws_lambda_function', details='', group='compute'), Resource(id='arn:aws:lambda:us-east-1:200984112386:function:aaaaaaaaaaaaa', name='aaaaaaaaaaaaa', type='aws_lambda_function', details='', group='compute')], [], [], [], [], [], [], [], [Resource(id='igw-09cc041a3f6e7d38b', name='igw-09cc041a3f6e7d38b', type='aws_internet_gateway', details='', group='network')], [Resource(id='acl-01a0765c917e4e733', name='acl-01a0765c917e4e733', type='aws_network_acl', details='NACL using Subnets subnet-0267b72fb6dead183, subnet-023da38a98c179cce, subnet-0c63113a164c83e0b', group='network')], [], [Resource(id='rtb-0405795a9a7f730e8', name='rtb-0405795a9a7f730e8', type='aws_route_table', details='', group='network'), Resource(id='rtb-0bf969c6f52d3ca40', name='rtb-0bf969c6f52d3ca40', type='aws_route_table', details='', group='network')], [Resource(id='sg-0521cf0ebff65c70d', name='ElasticMapReduce-slave', type='aws_security_group', details='', group='network'), Resource(id='sg-0abf4b1f1a9ecfe9c', name='MEUSG', type='aws_security_group', details='', group='network'), Resource(id='sg-0b21dea57386a36b4', name='ElasticMapReduce-master', type='aws_security_group', details='', group='network'), Resource(id='sg-0f2d79f705ff0d97d', name='default', type='aws_security_group', details='', group='network')], [Resource(id='subnet-0c63113a164c83e0b', name='subnet-0c63113a164c83e0b', type='aws_subnet', details='Subnet using CidrBlock 10.0.2.0/24 and AZ us-east-1e', group='network'), Resource(id='subnet-0267b72fb6dead183', name='subnet-0267b72fb6dead183', type='aws_subnet', details='Subnet using CidrBlock 10.0.3.0/24 and AZ us-east-1b', group='network'), Resource(id='subnet-023da38a98c179cce', name='subnet-023da38a98c179cce', type='aws_subnet', details='Subnet using CidrBlock 10.0.1.0/24 and AZ us-east-1a', group='network')], [], [], [], [], []]
        """ Check if assets/diagram directory exists """
        if not os.path.isdir(PATH_DIAGRAM_OUTPUT):
            print("OI")
            try:
                os.mkdir(PATH_DIAGRAM_OUTPUT)
            except OSError:
                print ("Creation of the directory %s failed" % PATH_DIAGRAM_OUTPUT)
            else:
                print ("Successfully created the directory %s " % PATH_DIAGRAM_OUTPUT)

        """ Ordering Resource list to group resources into cluster """
        ordered_resources = dict()
        for alldata in self.resources:
            if isinstance(alldata, list):
                for rundata in alldata:
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
        with Diagram(name="AWS VPC {} Resources".format(self.vpc_id), filename=PATH_DIAGRAM_OUTPUT+self.vpc_id, 
                     show=self.diagram, direction="TB"):
   
            """ VPC to represent main resource """
            _vpc = VPC("VPC {}".format(self.vpc_id))

            """ Iterate resources to draw it """
            for alldata in ordered_resources:
                with Cluster(alldata.capitalize() + " resources"):
                    for rundata in ordered_resources[alldata]:
                        resource_id.append(eval(Mapsources.mapresources.get(rundata["type"]))(rundata["name"]))


            """ Connecting resources and vpc """
            for resource in resource_id:
                resource >> _vpc
