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
from shared.common_aws import resource_tags, get_name_tag
from shared.error_handler import exception


class WORKSPACES(ResourceProvider):
    def __init__(self, vpc_options: VpcOptions):
        """
        Workspaces

        :param vpc_options:
        """
        super().__init__()
        self.vpc_options = vpc_options

    @exception
    @ResourceAvailable(services="workspaces")
    def get_resources(self) -> List[Resource]:

        client = self.vpc_options.client("workspaces")

        resources_found = []

        response = client.describe_workspaces()

        if self.vpc_options.verbose:
            message_handler("Collecting data from Workspaces...", "HEADER")

        for data in response["Workspaces"]:

            # Get tag name
            tags = client.describe_tags(ResourceId=data["WorkspaceId"])
            nametag = get_name_tag(tags)

            workspace_name = data["WorkspaceId"] if nametag is None else nametag

            directory_service = self.vpc_options.client("ds")
            directories = directory_service.describe_directories(
                DirectoryIds=[data["DirectoryId"]]
            )

            for directorie in directories["DirectoryDescriptions"]:

                if "VpcSettings" in directorie:

                    if directorie["VpcSettings"]["VpcId"] == self.vpc_options.vpc_id:
                        workspace_digest = ResourceDigest(
                            id=data["WorkspaceId"], type="aws_workspaces"
                        )
                        resources_found.append(
                            Resource(
                                digest=workspace_digest,
                                name=workspace_name,
                                details="",
                                group="enduser",
                                tags=resource_tags(tags),
                            )
                        )

                        self.relations_found.append(
                            ResourceEdge(
                                from_node=workspace_digest,
                                to_node=ResourceDigest(
                                    id=directorie["DirectoryId"], type="aws_ds"
                                ),
                            )
                        )

        return resources_found
