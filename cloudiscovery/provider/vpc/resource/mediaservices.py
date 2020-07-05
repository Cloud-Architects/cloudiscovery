import json
from typing import List

from provider.vpc.command import VpcOptions, check_ipvpc_inpolicy
from shared.common import (
    ResourceProvider,
    Resource,
    message_handler,
    ResourceDigest,
    ResourceEdge,
    datetime_to_string,
    ResourceAvailable,
)
from shared.common_aws import describe_subnet, resource_tags
from shared.error_handler import exception


class MEDIACONNECT(ResourceProvider):
    def __init__(self, vpc_options: VpcOptions):
        """
        Mediaconnect

        :param vpc_options:
        """
        super().__init__()
        self.vpc_options = vpc_options

    @exception
    @ResourceAvailable(services="mediaconnect")
    def get_resources(self) -> List[Resource]:

        client = self.vpc_options.client("mediaconnect")

        resources_found = []

        response = client.list_flows()

        if self.vpc_options.verbose:
            message_handler("Collecting data from Media Connect...", "HEADER")

        for data in response["Flows"]:
            tags_response = client.list_tags_for_resource(ResourceArn=data["FlowArn"])

            data_flow = client.describe_flow(FlowArn=data["FlowArn"])

            if "VpcInterfaces" in data_flow["Flow"]:

                for data_interfaces in data_flow["Flow"]["VpcInterfaces"]:

                    # Using subnet to check VPC
                    subnets = describe_subnet(
                        vpc_options=self.vpc_options,
                        subnet_ids=data_interfaces["SubnetId"],
                    )

                    if subnets is not None:
                        if subnets["Subnets"][0]["VpcId"] == self.vpc_options.vpc_id:
                            digest = ResourceDigest(
                                id=data["FlowArn"], type="aws_media_connect"
                            )
                            resources_found.append(
                                Resource(
                                    digest=digest,
                                    name=data["Name"],
                                    details="Flow using VPC {} in VPC Interface {}".format(
                                        self.vpc_options.vpc_id, data_interfaces["Name"]
                                    ),
                                    group="mediaservices",
                                    tags=resource_tags(tags_response),
                                )
                            )
                            self.relations_found.append(
                                ResourceEdge(
                                    from_node=digest,
                                    to_node=ResourceDigest(
                                        id=data_interfaces["SubnetId"],
                                        type="aws_subnet",
                                    ),
                                )
                            )

        return resources_found


class MEDIALIVE(ResourceProvider):
    def __init__(self, vpc_options: VpcOptions):
        """
        Medialive

        :param vpc_options:
        """
        super().__init__()
        self.vpc_options = vpc_options

    @exception
    @ResourceAvailable(services="medialive")
    def get_resources(self) -> List[Resource]:

        client = self.vpc_options.client("medialive")

        resources_found = []

        response = client.list_inputs()

        if self.vpc_options.verbose:
            message_handler("Collecting data from Media Live Inputs...", "HEADER")

        for data in response["Inputs"]:
            tags_response = client.list_tags_for_resource(ResourceArn=data["Arn"])
            for destinations in data["Destinations"]:
                if "Vpc" in destinations:
                    # describe networkinterface to get VpcId
                    ec2 = self.vpc_options.client("ec2")

                    eni = ec2.describe_network_interfaces(
                        NetworkInterfaceIds=[destinations["Vpc"]["NetworkInterfaceId"]]
                    )

                    if eni["NetworkInterfaces"][0]["VpcId"] == self.vpc_options.vpc_id:
                        digest = ResourceDigest(id=data["Arn"], type="aws_media_live")
                        resources_found.append(
                            Resource(
                                digest=digest,
                                name="Input " + destinations["Ip"],
                                details="",
                                group="mediaservices",
                                tags=resource_tags(tags_response),
                            )
                        )
                        self.relations_found.append(
                            ResourceEdge(
                                from_node=digest, to_node=self.vpc_options.vpc_digest(),
                            )
                        )
        return resources_found


class MEDIASTORE(ResourceProvider):
    def __init__(self, vpc_options: VpcOptions):
        """
        Mediastore

        :param vpc_options:
        """
        super().__init__()
        self.vpc_options = vpc_options

    @exception
    @ResourceAvailable(services="mediastore")
    def get_resources(self) -> List[Resource]:

        client = self.vpc_options.client("mediastore")

        resources_found = []

        response = client.list_containers()

        if self.vpc_options.verbose:
            message_handler("Collecting data from Media Store...", "HEADER")

        for data in response["Containers"]:

            store_queue_policy = client.get_container_policy(ContainerName=data["Name"])

            document = json.dumps(
                store_queue_policy["Policy"], default=datetime_to_string
            )

            ipvpc_found = check_ipvpc_inpolicy(
                document=document, vpc_options=self.vpc_options
            )

            if ipvpc_found is not False:
                tags_response = client.list_tags_for_resource(Resource=data["ARN"])
                digest = ResourceDigest(id=data["ARN"], type="aws_mediastore_polocy")
                resources_found.append(
                    Resource(
                        digest=digest,
                        name=data["Name"],
                        details="",
                        group="mediaservices",
                        tags=resource_tags(tags_response),
                    )
                )
                self.relations_found.append(
                    ResourceEdge(
                        from_node=digest, to_node=self.vpc_options.vpc_digest()
                    )
                )
        return resources_found
