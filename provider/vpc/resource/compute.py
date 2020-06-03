from provider.vpc.command import VpcOptions
from shared.common import *
from shared.error_handler import exception


class LAMBDA(ResourceProvider):

    def __init__(self, vpc_options: VpcOptions):
        super().__init__()
        self.vpc_options = vpc_options

    @exception
    def get_resources(self) -> List[Resource]:
        client = self.vpc_options.client('lambda')

        message_handler("Collecting data from Lambda Functions...", "HEADER")

        paginator = client.get_paginator('list_functions')
        pages = paginator.paginate()

        resources_found = []
        for response in pages:
            for data in response["Functions"]:
                if 'VpcConfig' in data and data['VpcConfig']['VpcId'] == self.vpc_options.vpc_id:
                    lambda_digest = ResourceDigest(id=data['FunctionArn'], type='aws_lambda_function')
                    for subnet_id in data['VpcConfig']['SubnetIds']:
                        self.relations_found.append(ResourceEdge(from_node=lambda_digest,
                                                                 to_node=ResourceDigest(id=subnet_id,
                                                                                        type='aws_subnet')))
                    resources_found.append(Resource(digest=lambda_digest,
                                                    name=data["FunctionName"],
                                                    details='',
                                                    group='compute'))

        return resources_found


class EC2(ResourceProvider):

    def __init__(self, vpc_options: VpcOptions):
        super().__init__()
        self.vpc_options = vpc_options

    @exception
    def get_resources(self) -> List[Resource]:

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

                            ec2_digest = ResourceDigest(id=instances['InstanceId'], type='aws_instance')
                            resources_found.append(Resource(digest=ec2_digest,
                                                            name=instance_name,
                                                            details='',
                                                            group='compute'))
                            self.relations_found.append(ResourceEdge(from_node=ec2_digest,
                                                                     to_node=ResourceDigest(id=instances['SubnetId'],
                                                                                            type='aws_subnet')))

        return resources_found


class EKS(ResourceProvider):

    def __init__(self, vpc_options: VpcOptions):
        super().__init__()
        self.vpc_options = vpc_options

    @exception
    def get_resources(self) -> List[Resource]:

        client = self.vpc_options.client('eks')

        resources_found = []

        response = client.list_clusters()

        message_handler("Collecting data from EKS Clusters...", "HEADER")

        if len(response["clusters"]) > 0:

            for data in response["clusters"]:

                cluster = client.describe_cluster(name=data)

                if cluster['cluster']['resourcesVpcConfig']['vpcId'] == self.vpc_options.vpc_id:
                    resources_found.append(Resource(digest=ResourceDigest(id=cluster['cluster']['arn'],
                                                                          type='aws_eks_cluster'),
                                                    name=cluster['cluster']["name"],
                                                    details='',
                                                    group='compute'))

        return resources_found


class EMR(ResourceProvider):

    def __init__(self, vpc_options: VpcOptions):
        super().__init__()
        self.vpc_options = vpc_options

    @exception
    def get_resources(self) -> List[Resource]:

        client = self.vpc_options.client('emr')

        resources_found = []

        response = client.list_clusters()

        message_handler("Collecting data from EMR Clusters...", "HEADER")

        if len(response["Clusters"]) > 0:

            for data in response["Clusters"]:

                cluster = client.describe_cluster(ClusterId=data['Id'])

                """ Using subnet to check VPC """
                ec2 = self.vpc_options.client('ec2')

                subnets = ec2.describe_subnets(SubnetIds=[cluster['Cluster']['Ec2InstanceAttributes']['Ec2SubnetId']])

                if subnets['Subnets'][0]['VpcId'] == self.vpc_options.vpc_id:
                    resources_found.append(Resource(digest=ResourceDigest(id=data['Id'],
                                                                          type='aws_emr_cluster'),
                                                    name=data['Name'],
                                                    details='',
                                                    group='compute'))

        return resources_found


class AUTOSCALING(ResourceProvider):

    def __init__(self, vpc_options: VpcOptions):
        super().__init__()
        self.vpc_options = vpc_options

    @exception
    def get_resources(self) -> List[Resource]:

        client = self.vpc_options.client('autoscaling')

        resources_found = []

        response = client.describe_auto_scaling_groups()

        message_handler("Collecting data from Autoscaling Groups...", "HEADER")

        if len(response["AutoScalingGroups"]) == 0:

            for data in response["AutoScalingGroups"]:

                asg_subnets = data['VPCZoneIdentifier'].split(",")

                """ describe subnet to get VpcId """
                ec2 = self.vpc_options.client('ec2')

                subnets = ec2.describe_subnets(SubnetIds=asg_subnets)

                """ Iterate subnet to get VPC """
                for data_subnet in subnets['Subnets']:

                    if data_subnet['VpcId'] == self.vpc_options.vpc_id:
                        resources_found.append(Resource(
                            digest=ResourceDigest(id=data['AutoScalingGroupARN'], type='aws_autoscaling_group'),
                            name=data['AutoScalingGroupName'],
                            details='Using LaunchConfigurationName {0}'.format(
                                data["LaunchConfigurationName"]),
                            group='compute'))

        return resources_found
