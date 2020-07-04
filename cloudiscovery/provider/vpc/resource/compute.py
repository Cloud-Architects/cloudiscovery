from typing import List

from provider.vpc.command import VpcOptions
from shared.common import (
    ResourceProvider,
    Resource,
    message_handler,
    ResourceDigest,
    ResourceEdge,
    ResourceAvailable,
)
from shared.common_aws import describe_subnet, resource_tags, get_name_tag, get_tag
from shared.error_handler import exception


class LAMBDA(ResourceProvider):
    def __init__(self, vpc_options: VpcOptions):
        """
        Lambda

        :param vpc_options:
        """
        super().__init__()
        self.vpc_options = vpc_options

    @exception
    @ResourceAvailable(services="lambda")
    def get_resources(self) -> List[Resource]:
        client = self.vpc_options.client("lambda")

        if self.vpc_options.verbose:
            message_handler("Collecting data from Lambda Functions...", "HEADER")

        paginator = client.get_paginator("list_functions")
        pages = paginator.paginate()

        resources_found = []
        for response in pages:
            for data in response["Functions"]:
                if (
                    "VpcConfig" in data
                    and data["VpcConfig"]["VpcId"] == self.vpc_options.vpc_id
                ):
                    lambda_digest = ResourceDigest(
                        id=data["FunctionArn"], type="aws_lambda_function"
                    )
                    for subnet_id in data["VpcConfig"]["SubnetIds"]:
                        self.relations_found.append(
                            ResourceEdge(
                                from_node=lambda_digest,
                                to_node=ResourceDigest(id=subnet_id, type="aws_subnet"),
                            )
                        )
                    list_tags_response = client.list_tags(Resource=data["FunctionArn"])

                    resources_found.append(
                        Resource(
                            digest=lambda_digest,
                            name=data["FunctionName"],
                            details="",
                            group="compute",
                            tags=resource_tags(list_tags_response),
                        )
                    )

        return resources_found


class EC2(ResourceProvider):
    def __init__(self, vpc_options: VpcOptions):
        """
        Ec2

        :param vpc_options:
        """
        super().__init__()
        self.vpc_options = vpc_options

    @exception
    @ResourceAvailable(services="ec2")
    def get_resources(self) -> List[Resource]:

        client = self.vpc_options.client("ec2")

        resources_found = []

        response = client.describe_instances()

        if self.vpc_options.verbose:
            message_handler("Collecting data from EC2 Instances...", "HEADER")

        for data in response["Reservations"]:
            for instances in data["Instances"]:

                if "VpcId" in instances:
                    if instances["VpcId"] == self.vpc_options.vpc_id:
                        nametag = get_name_tag(instances)
                        asg_name = get_tag(instances, "aws:autoscaling:groupName")

                        instance_name = (
                            instances["InstanceId"] if nametag is None else nametag
                        )

                        ec2_digest = ResourceDigest(
                            id=instances["InstanceId"], type="aws_instance"
                        )
                        resources_found.append(
                            Resource(
                                digest=ec2_digest,
                                name=instance_name,
                                details="",
                                group="compute",
                                tags=resource_tags(instances),
                            )
                        )
                        self.relations_found.append(
                            ResourceEdge(
                                from_node=ec2_digest,
                                to_node=ResourceDigest(
                                    id=instances["SubnetId"], type="aws_subnet"
                                ),
                            )
                        )
                        if asg_name is not None:
                            self.relations_found.append(
                                ResourceEdge(
                                    from_node=ec2_digest,
                                    to_node=ResourceDigest(
                                        id=asg_name, type="aws_autoscaling_group"
                                    ),
                                )
                            )

        return resources_found


class EKS(ResourceProvider):
    def __init__(self, vpc_options: VpcOptions):
        """
        Eks

        :param vpc_options:
        """
        super().__init__()
        self.vpc_options = vpc_options

    @exception
    @ResourceAvailable(services="eks")
    def get_resources(self) -> List[Resource]:

        client = self.vpc_options.client("eks")

        resources_found = []

        response = client.list_clusters()

        if self.vpc_options.verbose:
            message_handler("Collecting data from EKS Clusters...", "HEADER")

        for data in response["clusters"]:

            cluster = client.describe_cluster(name=data)

            if (
                cluster["cluster"]["resourcesVpcConfig"]["vpcId"]
                == self.vpc_options.vpc_id
            ):
                digest = ResourceDigest(
                    id=cluster["cluster"]["arn"], type="aws_eks_cluster"
                )
                resources_found.append(
                    Resource(
                        digest=digest,
                        name=cluster["cluster"]["name"],
                        details="",
                        group="compute",
                        tags=resource_tags(data),
                    )
                )
                for subnet_id in cluster["cluster"]["resourcesVpcConfig"]["subnetIds"]:
                    self.relations_found.append(
                        ResourceEdge(
                            from_node=digest,
                            to_node=ResourceDigest(id=subnet_id, type="aws_subnet"),
                        )
                    )

        return resources_found


class EMR(ResourceProvider):
    def __init__(self, vpc_options: VpcOptions):
        """
        Emr

        :param vpc_options:
        """
        super().__init__()
        self.vpc_options = vpc_options

    @exception
    @ResourceAvailable(services="emr")
    def get_resources(self) -> List[Resource]:

        client = self.vpc_options.client("emr")

        resources_found = []

        response = client.list_clusters()

        if self.vpc_options.verbose:
            message_handler("Collecting data from EMR Clusters...", "HEADER")

        for data in response["Clusters"]:

            cluster = client.describe_cluster(ClusterId=data["Id"])

            # Using subnet to check VPC
            subnets = describe_subnet(
                vpc_options=self.vpc_options,
                subnet_ids=cluster["Cluster"]["Ec2InstanceAttributes"]["Ec2SubnetId"],
            )

            if subnets is not None:

                if subnets["Subnets"][0]["VpcId"] == self.vpc_options.vpc_id:
                    digest = ResourceDigest(id=data["Id"], type="aws_emr_cluster")
                    resources_found.append(
                        Resource(
                            digest=digest,
                            name=data["Name"],
                            details="",
                            group="compute",
                            tags=resource_tags(cluster["Cluster"]),
                        )
                    )
                    self.relations_found.append(
                        ResourceEdge(
                            from_node=digest,
                            to_node=ResourceDigest(
                                id=cluster["Cluster"]["Ec2InstanceAttributes"][
                                    "Ec2SubnetId"
                                ],
                                type="aws_subnet",
                            ),
                        )
                    )

        return resources_found


class AUTOSCALING(ResourceProvider):
    def __init__(self, vpc_options: VpcOptions):
        """
        Autoscaling

        :param vpc_options:
        """
        super().__init__()
        self.vpc_options = vpc_options

    @exception
    @ResourceAvailable(services="autoscaling")
    def get_resources(self) -> List[Resource]:

        client = self.vpc_options.client("autoscaling")

        resources_found = []

        response = client.describe_auto_scaling_groups()

        if self.vpc_options.verbose:
            message_handler("Collecting data from Autoscaling Groups...", "HEADER")

        for data in response["AutoScalingGroups"]:

            asg_subnets = data["VPCZoneIdentifier"].split(",")

            # Using subnet to check VPC
            subnets = describe_subnet(
                vpc_options=self.vpc_options, subnet_ids=asg_subnets
            )

            if subnets is not None:
                # Iterate subnet to get VPC
                for data_subnet in subnets["Subnets"]:

                    if data_subnet["VpcId"] == self.vpc_options.vpc_id:
                        asg_name = data["AutoScalingGroupName"]
                        digest = ResourceDigest(
                            id=asg_name, type="aws_autoscaling_group"
                        )
                        resources_found.append(
                            Resource(
                                digest=digest,
                                name=asg_name,
                                details="Using LaunchConfigurationName {0}".format(
                                    data["LaunchConfigurationName"]
                                ),
                                group="compute",
                                tags=resource_tags(data),
                            )
                        )
                        self.relations_found.append(
                            ResourceEdge(
                                from_node=digest,
                                to_node=ResourceDigest(
                                    id=data_subnet["SubnetId"], type="aws_subnet"
                                ),
                            )
                        )

        return resources_found
