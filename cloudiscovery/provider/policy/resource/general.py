from typing import List

from provider.policy.command import PolicyOptions
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


class IamUser(ResourceProvider):
    @ResourceAvailable(services="iam")
    def __init__(self, options: PolicyOptions):
        """
        Iam user

        :param options:
        """
        super().__init__()
        self.options = options
        self.client = options.client("iam")
        self.users_found: List[Resource] = []

    @exception
    def get_resources(self) -> List[Resource]:
        if self.options.verbose:
            message_handler("Collecting data from IAM Users...", "HEADER")
        paginator = self.client.get_paginator("list_users")
        pages = paginator.paginate()

        users_found = []
        for users in pages:
            for data in users["Users"]:
                tag_response = self.client.list_user_tags(UserName=data["UserName"],)
                users_found.append(
                    Resource(
                        digest=ResourceDigest(id=data["UserName"], type="aws_iam_user"),
                        name=data["UserName"],
                        details="",
                        group="User",
                        tags=resource_tags(tag_response),
                    )
                )
        self.users_found = users_found
        return users_found

    @exception
    def get_relations(self) -> List[ResourceEdge]:
        resources_found = []
        for user in self.users_found:
            response = self.client.list_groups_for_user(UserName=user.name)
            for group in response["Groups"]:
                resources_found.append(
                    ResourceEdge(
                        from_node=user.digest,
                        to_node=ResourceDigest(
                            id=group["GroupName"], type="aws_iam_group"
                        ),
                    )
                )

            response = self.client.list_attached_user_policies(UserName=user.name)
            for policy in response["AttachedPolicies"]:
                resources_found.append(
                    ResourceEdge(
                        from_node=user.digest,
                        to_node=ResourceDigest(
                            id=policy["PolicyArn"], type="aws_iam_policy"
                        ),
                    )
                )

        return resources_found
