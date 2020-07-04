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


class DIRECTORYSERVICE(ResourceProvider):
    def __init__(self, vpc_options: VpcOptions):
        """
        Directory service

        :param vpc_options:
        """
        super().__init__()
        self.vpc_options = vpc_options

    @exception
    @ResourceAvailable(services="ds")
    def get_resources(self) -> List[Resource]:

        client = self.vpc_options.client("ds")

        resources_found = []

        response = client.describe_directories()

        if self.vpc_options.verbose:
            message_handler("Collecting data from Directory Services...", "HEADER")

        for data in response["DirectoryDescriptions"]:

            if "VpcSettings" in data:

                if data["VpcSettings"]["VpcId"] == self.vpc_options.vpc_id:
                    directory_service_digest = ResourceDigest(
                        id=data["DirectoryId"], type="aws_ds"
                    )
                    resources_found.append(
                        Resource(
                            digest=directory_service_digest,
                            name=data["Name"],
                            details="",
                            group="identity",
                            tags=resource_tags(data),
                        )
                    )

                    for subnet in data["VpcSettings"]["SubnetIds"]:
                        self.relations_found.append(
                            ResourceEdge(
                                from_node=directory_service_digest,
                                to_node=ResourceDigest(id=subnet, type="aws_subnet"),
                            )
                        )

        return resources_found
