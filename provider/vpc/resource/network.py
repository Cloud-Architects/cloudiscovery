from typing import List

from provider.vpc.command import VpcOptions
from shared.common import (
    ResourceProvider,
    Resource,
    message_handler,
    get_name_tags,
    ResourceDigest,
    ResourceEdge,
)
from shared.error_handler import exception


class INTERNETGATEWAY(ResourceProvider):
    def __init__(self, vpc_options: VpcOptions):
        super().__init__()
        self.vpc_options = vpc_options

    @exception
    def get_resources(self) -> List[Resource]:
        client = self.vpc_options.client("ec2")

        resources_found = []

        filters = [{"Name": "attachment.vpc-id", "Values": [self.vpc_options.vpc_id]}]

        response = client.describe_internet_gateways(Filters=filters)

        message_handler("Collecting data from Internet Gateways...", "HEADER")

        """ One VPC has only 1 IGW then it's a direct check """
        if len(response["InternetGateways"]) > 0:
            nametags = get_name_tags(response)

            name = (
                response["InternetGateways"][0]["InternetGatewayId"]
                if nametags is False
                else nametags
            )

            igw_digest = ResourceDigest(
                id=response["InternetGateways"][0]["InternetGatewayId"],
                type="aws_internet_gateway",
            )
            resources_found.append(
                Resource(digest=igw_digest, name=name, details="", group="network")
            )
            self.relations_found.append(
                ResourceEdge(
                    from_node=igw_digest, to_node=self.vpc_options.vpc_digest()
                )
            )

        return resources_found


class NATGATEWAY(ResourceProvider):
    def __init__(self, vpc_options: VpcOptions):
        super().__init__()
        self.vpc_options = vpc_options

    @exception
    def get_resources(self) -> List[Resource]:

        client = self.vpc_options.client("ec2")

        resources_found = []

        filters = [{"Name": "vpc-id", "Values": [self.vpc_options.vpc_id]}]

        response = client.describe_nat_gateways(Filters=filters)

        message_handler("Collecting data from NAT Gateways...", "HEADER")

        if len(response["NatGateways"]) > 0:

            for data in response["NatGateways"]:

                if data["VpcId"] == self.vpc_options.vpc_id:
                    nametags = get_name_tags(data)

                    name = data["NatGatewayId"] if nametags is False else nametags

                    nat_digest = ResourceDigest(
                        id=data["NatGatewayId"], type="aws_nat_gateway"
                    )
                    resources_found.append(
                        Resource(
                            digest=nat_digest,
                            name=name,
                            details="NAT Gateway Private IP {}, Public IP {}, Subnet id {}".format(
                                data["NatGatewayAddresses"][0]["PrivateIp"],
                                data["NatGatewayAddresses"][0]["PublicIp"],
                                data["SubnetId"],
                            ),
                            group="network",
                        )
                    )
                    self.relations_found.append(
                        ResourceEdge(
                            from_node=nat_digest,
                            to_node=ResourceDigest(
                                id=data["SubnetId"], type="aws_subnet"
                            ),
                        )
                    )

        return resources_found


class ELASTICLOADBALANCING(ResourceProvider):
    def __init__(self, vpc_options: VpcOptions):
        super().__init__()
        self.vpc_options = vpc_options

    @exception
    def get_resources(self) -> List[Resource]:

        client = self.vpc_options.client("elb")

        resources_found = []

        response = client.describe_load_balancers()

        message_handler("Collecting data from Classic Load Balancers...", "HEADER")

        if len(response["LoadBalancerDescriptions"]) > 0:

            for data in response["LoadBalancerDescriptions"]:
                if data["VPCId"] == self.vpc_options.vpc_id:
                    elb_digest = ResourceDigest(
                        id=data["LoadBalancerName"], type="aws_elb_classic"
                    )
                    for subnet_id in data["Subnets"]:
                        self.relations_found.append(
                            ResourceEdge(
                                from_node=elb_digest,
                                to_node=ResourceDigest(id=subnet_id, type="aws_subnet"),
                            )
                        )
                    resources_found.append(
                        Resource(
                            digest=elb_digest,
                            name=data["LoadBalancerName"],
                            details="",
                            group="network",
                        )
                    )

        return resources_found


class ELASTICLOADBALANCINGV2(ResourceProvider):
    def __init__(self, vpc_options: VpcOptions):
        super().__init__()
        self.vpc_options = vpc_options

    @exception
    def get_resources(self) -> List[Resource]:

        client = self.vpc_options.client("elbv2")

        resources_found = []

        response = client.describe_load_balancers()

        message_handler("Collecting data from Application Load Balancers...", "HEADER")

        if len(response["LoadBalancers"]) > 0:

            for data in response["LoadBalancers"]:

                if data["VpcId"] == self.vpc_options.vpc_id:
                    elb_digest = ResourceDigest(
                        id=data["LoadBalancerName"], type="aws_elb"
                    )

                    subnet_ids = []
                    for availabilityZone in data["AvailabilityZones"]:
                        subnet_ids.append(availabilityZone["SubnetId"])
                        self.relations_found.append(
                            ResourceEdge(
                                from_node=elb_digest,
                                to_node=ResourceDigest(
                                    id=availabilityZone["SubnetId"], type="aws_subnet"
                                ),
                            )
                        )

                    resources_found.append(
                        Resource(
                            digest=elb_digest,
                            name=data["LoadBalancerName"],
                            details="",
                            group="network",
                        )
                    )

        return resources_found


class RouteTable(ResourceProvider):
    def __init__(self, vpc_options: VpcOptions):
        super().__init__()
        self.vpc_options = vpc_options

    @exception
    def get_resources(self) -> List[Resource]:

        client = self.vpc_options.client("ec2")

        resources_found = []

        filters = [{"Name": "vpc-id", "Values": [self.vpc_options.vpc_id]}]

        response = client.describe_route_tables(Filters=filters)

        message_handler("Collecting data from Route Tables...", "HEADER")

        """ Iterate to get all route table filtered """
        for data in response["RouteTables"]:
            nametags = get_name_tags(data)

            name = data["RouteTableId"] if nametags is False else nametags
            table_digest = ResourceDigest(
                id=data["RouteTableId"], type="aws_route_table"
            )
            is_main = False
            for association in data["Associations"]:
                if association["Main"] is True:
                    is_main = True
            if is_main:
                self.relations_found.append(
                    ResourceEdge(
                        from_node=table_digest, to_node=self.vpc_options.vpc_digest(),
                    )
                )
            else:
                for association in data["Associations"]:
                    if "SubnetId" in association:
                        self.relations_found.append(
                            ResourceEdge(
                                from_node=table_digest,
                                to_node=ResourceDigest(
                                    id=association["SubnetId"], type="aws_subnet"
                                ),
                            )
                        )

            is_public = False

            for route in data["Routes"]:
                if (
                    "DestinationCidrBlock" in route
                    and route["DestinationCidrBlock"] == "0.0.0.0/0"
                    and "GatewayId" in route
                    and route["GatewayId"].startswith("igw-")
                ):
                    is_public = True

            resources_found.append(
                Resource(
                    digest=table_digest,
                    name=name,
                    details="default: {}, public: {}".format(is_main, is_public),
                    group="network",
                )
            )
        return resources_found


class SUBNET(ResourceProvider):
    def __init__(self, vpc_options: VpcOptions):
        super().__init__()
        self.vpc_options = vpc_options

    @exception
    def get_resources(self) -> List[Resource]:

        client = self.vpc_options.client("ec2")

        resources_found = []

        filters = [{"Name": "vpc-id", "Values": [self.vpc_options.vpc_id]}]

        response = client.describe_subnets(Filters=filters)

        message_handler("Collecting data from Subnets...", "HEADER")

        if len(response["Subnets"]) > 0:

            """ Iterate to get all route table filtered """
            for data in response["Subnets"]:
                nametags = get_name_tags(data)

                name = data["SubnetId"] if nametags is False else nametags

                subnet_digest = ResourceDigest(id=data["SubnetId"], type="aws_subnet")
                resources_found.append(
                    Resource(
                        digest=subnet_digest,
                        name=name,
                        details="Subnet using CidrBlock {} and AZ {}".format(
                            data["CidrBlock"], data["AvailabilityZone"]
                        ),
                        group="network",
                    )
                )

                self.relations_found.append(
                    ResourceEdge(
                        from_node=subnet_digest, to_node=self.vpc_options.vpc_digest()
                    )
                )

        return resources_found


class NACL(ResourceProvider):
    def __init__(self, vpc_options: VpcOptions):
        super().__init__()
        self.vpc_options = vpc_options

    @exception
    def get_resources(self) -> List[Resource]:

        client = self.vpc_options.client("ec2")

        resources_found = []

        filters = [{"Name": "vpc-id", "Values": [self.vpc_options.vpc_id]}]

        response = client.describe_network_acls(Filters=filters)

        message_handler("Collecting data from NACLs...", "HEADER")

        if len(response["NetworkAcls"]) > 0:

            """ Iterate to get all NACL filtered """
            for data in response["NetworkAcls"]:
                nacl_digest = ResourceDigest(
                    id=data["NetworkAclId"], type="aws_network_acl"
                )

                subnet_ids = []
                for subnet in data["Associations"]:
                    subnet_ids.append(subnet["SubnetId"])
                    self.relations_found.append(
                        ResourceEdge(
                            from_node=nacl_digest,
                            to_node=ResourceDigest(
                                id=subnet["SubnetId"], type="aws_subnet"
                            ),
                        )
                    )

                nametags = get_name_tags(data)
                name = data["NetworkAclId"] if nametags is False else nametags
                resources_found.append(
                    Resource(
                        digest=nacl_digest,
                        name=name,
                        details="NACL using Subnets {}".format(", ".join(subnet_ids)),
                        group="network",
                    )
                )

        return resources_found


class SECURITYGROUP(ResourceProvider):
    def __init__(self, vpc_options: VpcOptions):
        super().__init__()
        self.vpc_options = vpc_options

    @exception
    def get_resources(self) -> List[Resource]:

        client = self.vpc_options.client("ec2")

        resources_found = []

        filters = [{"Name": "vpc-id", "Values": [self.vpc_options.vpc_id]}]

        response = client.describe_security_groups(Filters=filters)

        message_handler("Collecting data from Security Groups...", "HEADER")

        if len(response["SecurityGroups"]) > 0:

            """ Iterate to get all SG filtered """
            for data in response["SecurityGroups"]:
                group_digest = ResourceDigest(
                    id=data["GroupId"], type="aws_security_group"
                )
                resources_found.append(
                    Resource(
                        digest=group_digest,
                        name=data["GroupName"],
                        details="",
                        group="network",
                    )
                )
                self.relations_found.append(
                    ResourceEdge(
                        from_node=group_digest, to_node=self.vpc_options.vpc_digest()
                    )
                )

        return resources_found


class VPCPEERING(ResourceProvider):
    def __init__(self, vpc_options: VpcOptions):
        super().__init__()
        self.vpc_options = vpc_options

    @exception
    def get_resources(self) -> List[Resource]:

        client = self.vpc_options.client("ec2")

        resources_found = []

        response = client.describe_vpc_peering_connections()

        message_handler("Collecting data from VPC Peering...", "HEADER")

        if len(response["VpcPeeringConnections"]) > 0:

            """ Iterate to get all vpc peering and check either accepter or requester """
            for data in response["VpcPeeringConnections"]:

                if (
                    data["AccepterVpcInfo"]["VpcId"] == self.vpc_options.vpc_id
                    or data["RequesterVpcInfo"]["VpcId"] == self.vpc_options.vpc_id
                ):
                    nametags = get_name_tags(data)

                    name = (
                        data["VpcPeeringConnectionId"]
                        if nametags is False
                        else nametags
                    )

                    peering_digest = ResourceDigest(
                        id=data["VpcPeeringConnectionId"],
                        type="aws_vpc_peering_connection",
                    )
                    resources_found.append(
                        Resource(
                            digest=peering_digest,
                            name=name,
                            details="Vpc Peering Accepter OwnerId {}, Accepter Region {}, Accepter VpcId {} \
                                                             Requester OwnerId {}, Requester Region {}, \
                                                             Requester VpcId {}".format(
                                data["AccepterVpcInfo"]["OwnerId"],
                                data["AccepterVpcInfo"]["Region"],
                                data["AccepterVpcInfo"]["VpcId"],
                                data["RequesterVpcInfo"]["OwnerId"],
                                data["RequesterVpcInfo"]["Region"],
                                data["RequesterVpcInfo"]["VpcId"],
                            ),
                            group="network",
                        )
                    )
                    self.relations_found.append(
                        ResourceEdge(
                            from_node=peering_digest,
                            to_node=self.vpc_options.vpc_digest(),
                        )
                    )
        return resources_found


class VPC(ResourceProvider):
    def __init__(self, vpc_options: VpcOptions):
        super().__init__()
        self.vpc_options = vpc_options

    @exception
    def get_resources(self) -> List[Resource]:
        return [
            Resource(digest=self.vpc_options.vpc_digest(), name=self.vpc_options.vpc_id)
        ]


class VPCENDPOINT(ResourceProvider):
    def __init__(self, vpc_options: VpcOptions):
        super().__init__()
        self.vpc_options = vpc_options

    @exception
    def get_resources(self) -> List[Resource]:

        client = self.vpc_options.client("ec2")

        resources_found = []

        filters = [{"Name": "vpc-id", "Values": [self.vpc_options.vpc_id]}]

        response = client.describe_vpc_endpoints(Filters=filters)

        message_handler("Collecting data from VPC Endpoints...", "HEADER")

        if len(response["VpcEndpoints"]) > 0:

            """ Iterate to get all VPCE filtered """
            for data in response["VpcEndpoints"]:

                if data["VpcId"] == self.vpc_options.vpc_id:
                    endpoint_digest = ResourceDigest(
                        id=data["VpcEndpointId"], type="aws_vpc_endpoint_gateway"
                    )
                    if data["VpcEndpointType"] == "Gateway":
                        resources_found.append(
                            Resource(
                                digest=endpoint_digest,
                                name=data["ServiceName"],
                                details="Vpc Endpoint Gateway RouteTable {}".format(
                                    ", ".join(data["RouteTableIds"])
                                ),
                                group="network",
                            )
                        )
                        self.relations_found.append(
                            ResourceEdge(
                                from_node=endpoint_digest,
                                to_node=self.vpc_options.vpc_digest(),
                            )
                        )
                    else:
                        resources_found.append(
                            Resource(
                                digest=endpoint_digest,
                                name=data["ServiceName"],
                                details="Vpc Endpoint Service Subnet {}".format(
                                    ", ".join(data["SubnetIds"])
                                ),
                                group="network",
                            )
                        )
                        for subnet_id in data["SubnetIds"]:
                            self.relations_found.append(
                                ResourceEdge(
                                    from_node=endpoint_digest,
                                    to_node=ResourceDigest(
                                        id=subnet_id, type="aws_subnet"
                                    ),
                                )
                            )

        return resources_found
