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
from shared.common_aws import resource_tags
from shared.error_handler import exception


class SYNTHETICSCANARIES(ResourceProvider):
    def __init__(self, vpc_options: VpcOptions):
        """
        Synthetic canaries

        :param vpc_options:
        """
        super().__init__()
        self.vpc_options = vpc_options

    @exception
    @ResourceAvailable(services="synthetics")
    def get_resources(self) -> List[Resource]:

        client = self.vpc_options.client("synthetics")

        resources_found = []

        response = client.describe_canaries()

        if self.vpc_options.verbose:
            message_handler("Collecting data from Synthetic Canaries...", "HEADER")

        for data in response["Canaries"]:

            # Check if VpcConfig is in dict
            if "VpcConfig" in data:

                if data["VpcConfig"]["VpcId"] == self.vpc_options.vpc_id:
                    digest = ResourceDigest(id=data["Id"], type="aws_canaries_function")
                    resources_found.append(
                        Resource(
                            digest=digest,
                            name=data["Name"],
                            details="",
                            group="management",
                            tags=resource_tags(data),
                        )
                    )
                    for subnet_id in data["VpcConfig"]["SubnetIds"]:
                        self.relations_found.append(
                            ResourceEdge(
                                from_node=digest,
                                to_node=ResourceDigest(id=subnet_id, type="aws_subnet"),
                            )
                        )

        return resources_found
