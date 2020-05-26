from typing import List

from shared.common import *
from shared.error_handler import exception


class LAMBDA(object):

    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    @exception
    def run(self) -> List[Resource]:

        client = self.vpc_options.client('lambda')

        resources_found = []

        response = client.list_functions()

        message_handler("Collecting data from LAMBDA FUNCTIONS...", "HEADER")

        if len(response["Functions"]) > 0:

            for data in response["Functions"]:
                if 'VpcConfig' in data and data['VpcConfig']['VpcId'] == self.vpc_options.vpc_id:
                    resources_found.append(Resource(id=data['FunctionArn'],
                                                    name=data["FunctionName"],
                                                    type='aws_lambda_function',
                                                    details='',
                                                    group='compute'))

        return resources_found


class EC2(object):

    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    @exception
    def run(self) -> List[Resource]:

        client = self.vpc_options.client('ec2')

        resources_found = []

        response = client.describe_instances()

        message_handler("Collecting data from EC2 Instances...", "HEADER")

        if len(response["Reservations"]) > 0:

            for data in response["Reservations"]:
                for instances in data['Instances']:

                    if "VpcId" in instances:
                        if instances['VpcId'] == self.vpc_options.vpc_id:
                            nametags = get_name_tags(instances)

                            instance_name = instances["InstanceId"] if nametags is False else nametags

                            resources_found.append(Resource(id=instances['InstanceId'],
                                                            name=instance_name,
                                                            type='aws_instance',
                                                            details='',
                                                            group='compute'))

        return resources_found


class EKS(object):

    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    @exception
    def run(self) -> List[Resource]:

        client = self.vpc_options.client('eks')

        resources_found = []

        response = client.list_clusters()

        message_handler("Collecting data from EKS CLUSTERS...", "HEADER")

        if len(response["clusters"]) > 0:

            for data in response["clusters"]:

                cluster = client.describe_cluster(name=data)

                if cluster['cluster']['resourcesVpcConfig']['vpcId'] == self.vpc_options.vpc_id:
                    resources_found.append(Resource(id=cluster['cluster']['arn'],
                                                    name=cluster['cluster']["name"],
                                                    type='aws_eks_cluster',
                                                    details='',
                                                    group='compute'))

        return resources_found


class EMR(object):

    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    @exception
    def run(self) -> List[Resource]:

        client = self.vpc_options.client('emr')

        resources_found = []

        response = client.list_clusters()

        message_handler("Collecting data from EMR CLUSTERS...", "HEADER")

        if len(response["Clusters"]) > 0:

            for data in response["Clusters"]:

                cluster = client.describe_cluster(ClusterId=data['Id'])

                """ Using subnet to check VPC """
                ec2 = self.vpc_options.client('ec2')

                subnets = ec2.describe_subnets(SubnetIds=[cluster['Cluster']['Ec2InstanceAttributes']['Ec2SubnetId']])

                if subnets['Subnets'][0]['VpcId'] == self.vpc_options.vpc_id:
                    resources_found.append(Resource(id=data['Id'],
                                                    name=data['Name'],
                                                    type='aws_emr_cluster',
                                                    details='',
                                                    group='compute'))

        return resources_found


class AUTOSCALING(object):

    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    @exception
    def run(self) -> List[Resource]:

        client = self.vpc_options.client('autoscaling')

        resources_found = []

        response = client.describe_auto_scaling_groups()

        message_handler("Collecting data from AUTOSCALING GROUPS...", "HEADER")

        if len(response["AutoScalingGroups"]) == 0:

            for data in response["AutoScalingGroups"]:

                asg_subnets = data['VPCZoneIdentifier'].split(",")

                """ describe subnet to get VpcId """
                ec2 = self.vpc_options.client('ec2')

                subnets = ec2.describe_subnets(SubnetIds=asg_subnets)

                """ Iterate subnet to get VPC """
                for data_subnet in subnets['Subnets']:

                    if data_subnet['VpcId'] == self.vpc_options.vpc_id:
                        resources_found.append(Resource(id=data['AutoScalingGroupARN'],
                                                        name=data['AutoScalingGroupName'],
                                                        type='aws_autoscaling_group',
                                                        details='Using LaunchConfigurationName {0}'.format(
                                                            data["LaunchConfigurationName"]),
                                                        group='compute'))

        return resources_found
