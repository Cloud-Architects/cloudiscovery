from typing import List

from provider.ibm.common_ibm import resource_tags
from provider.ibm.vpc.command import VpcOptions
from ibm_cloud_sdk_core import ApiException
from shared.common import (
    ResourceProvider,
    Resource,
    message_handler,
    ResourceDigest,
    ResourceEdge,
)
from shared.error_handler import exception


class RouteTable(ResourceProvider):
    def __init__(self, vpc_options: VpcOptions):
        """
        Route table

        :param vpc_options:
        """
        super().__init__()
        self.vpc_options = vpc_options

    @exception
    def get_resources(self) -> List[Resource]:

        service = self.vpc_options.service
        resources_found = []
        list_tables = service.list_vpc_routing_tables(
            self.vpc_options.vpc_id
        ).get_result()["routing_tables"]
        # Iterate to get all route table filtered
        for route_table in list_tables:
            name = route_table["id"]
            is_default = route_table["is_default"]
            table_digest = ResourceDigest(id=route_table["id"], type="ibm_route_table")

            self.relations_found.append(
                ResourceEdge(
                    from_node=table_digest,
                    to_node=self.vpc_options.vpc_digest(),
                )
            )

            list_routes = route_table["routes"]
            for response in list_routes:
                digest = ResourceDigest(id=response["id"], type="ibm_route")

                resources_found.append(
                    Resource(
                        digest=digest,
                        name=response["name"],
                        details="",
                        group="network",
                        tags=resource_tags(response),
                    )
                )
                self.relations_found.append(
                    ResourceEdge(
                        from_node=digest,
                        to_node=table_digest,
                    )
                )

            list_subnets = route_table["subnets"]

            for subnet in list_subnets:
                digest = ResourceDigest(id=subnet["id"], type="ibm_subnet")
                resources_found.append(
                    Resource(
                        digest=digest,
                        name=subnet["name"],
                        details="",
                        group="network",
                        tags=resource_tags(subnet),
                    )
                )
                self.relations_found.append(
                    ResourceEdge(
                        from_node=table_digest,
                        to_node=digest,
                    )
                )
                is_public = False
                try:
                    response = service.get_subnet_public_gateway(id=subnet["id"])
                    if response is not None:
                        if response["id"] is not None:
                            is_public = True
                            pgw_digest = ResourceDigest(
                                id=response["id"], type="ibm_public_gateway"
                            )
                            resources_found.append(
                                Resource(
                                    digest=pgw_digest,
                                    name=response["name"],
                                    details="public: {}".format(is_public),
                                    group="network",
                                    tags=resource_tags(response),
                                )
                            )
                            self.relations_found.append(
                                ResourceEdge(
                                    from_node=pgw_digest,
                                    to_node=digest,
                                )
                            )
                except ApiException:
                    print("No public gateway for subnet id " + subnet["id"])

            resources_found.append(
                Resource(
                    digest=table_digest,
                    name=name,
                    details="default: {}, public: {}".format(is_default, is_public),
                    group="network",
                    tags=resource_tags(route_table),
                )
            )
        return resources_found


class VPC(ResourceProvider):
    def __init__(self, vpc_options: VpcOptions):
        """
        Vpc

        :param vpc_options:
        """
        super().__init__()
        self.vpc_options = vpc_options

    @exception
    def get_resources(self) -> List[Resource]:
        # service = self.vpc_options.service
        # vpc_response = service.get_vpc(self.vpc_options.vpc_id)
        return [
            Resource(
                digest=self.vpc_options.vpc_digest(),
                name=self.vpc_options.vpc_id,
                tags="",
            )
        ]


class NACL(ResourceProvider):
    def __init__(self, vpc_options: VpcOptions):

        # Nacl

        # :param vpc_options:

        super().__init__()
        self.vpc_options = vpc_options

    @exception
    def get_resources(self) -> List[Resource]:

        service = self.vpc_options.service

        resources_found = []

        response = service.get_vpc_default_network_acl(
            id=self.vpc_options.vpc_id
        ).get_result()
        if self.vpc_options.verbose:
            message_handler("Collecting data from NACLs...", "HEADER")

        nacl_digest = ResourceDigest(id=response["id"], type="ibm_network_acl")
        subnet_ids = []
        for subnet in response["subnets"]:
            subnet_ids.append(subnet["id"])
            self.relations_found.append(
                ResourceEdge(
                    from_node=nacl_digest,
                    to_node=ResourceDigest(id=subnet["id"], type="ibm_subnet"),
                )
            )

        name = response["name"]

        resources_found.append(
            Resource(
                digest=nacl_digest,
                name=name,
                details="NACL using Subnets {}".format(", ".join(subnet_ids)),
                group="network",
                tags=resource_tags(response),
            )
        )

        return resources_found


class SECURITYGROUP(ResourceProvider):
    def __init__(self, vpc_options: VpcOptions):

        # Security group

        # :param vpc_options:

        super().__init__()
        self.vpc_options = vpc_options

    @exception
    def get_resources(self) -> List[Resource]:
        service = self.vpc_options.service
        response = service.list_security_groups(
            vpc_id=self.vpc_options.vpc_id
        ).get_result()
        resources_found = []

        if self.vpc_options.verbose:
            message_handler("Collecting data from Security Groups...", "HEADER")

        for data in response["security_groups"]:
            group_digest = ResourceDigest(id=data["id"], type="ibm_security_group")
            resources_found.append(
                Resource(
                    digest=group_digest,
                    name=data["name"],
                    details="",
                    group="network",
                    tags=resource_tags(data),
                )
            )
            self.relations_found.append(
                ResourceEdge(
                    from_node=group_digest, to_node=self.vpc_options.vpc_digest()
                )
            )

        return resources_found
