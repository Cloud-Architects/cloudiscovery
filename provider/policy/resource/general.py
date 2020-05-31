from provider.policy.command import ProfileOptions
from shared.common import *
from shared.error_handler import exception


class IamUser(ResourceProvider):

    def __init__(self, options: ProfileOptions):
        self.client = options.session.client('iam')
        self.users_found: List[Resource] = []

    @exception
    def get_resources(self) -> List[Resource]:
        message_handler("Collecting data from IAM Users...", "HEADER")
        paginator = self.client.get_paginator('list_users')
        pages = paginator.paginate()

        users_found = []
        for users in pages:
            for data in users['Users']:
                users_found.append(Resource(digest=ResourceDigest(id=data['UserName'], type='aws_iam_user'),
                                            name=data['UserName'],
                                            details='',
                                            group='User'))
        self.users_found = users_found
        return users_found

    @exception
    def get_relations(self) -> List[ResourceEdge]:
        resources_found = []
        for user in self.users_found:
            response = self.client.list_groups_for_user(
                UserName=user.name
            )
            for group in response['Groups']:
                resources_found.append(ResourceEdge(from_node=user.digest,
                                                    to_node=ResourceDigest(id=group['GroupName'],
                                                                           type='aws_iam_group')))

            response = self.client.list_attached_user_policies(
                UserName=user.name
            )
            for policy in response['AttachedPolicies']:
                resources_found.append(ResourceEdge(from_node=user.digest,
                                                    to_node=ResourceDigest(id=policy['PolicyArn'],
                                                                           type='aws_iam_policy')))

        return resources_found
