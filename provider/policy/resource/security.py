from provider.policy.command import ProfileOptions
from shared.common import *
from shared.error_handler import exception


class IAMPOLICY(ResourceProvider):

    def __init__(self, options: ProfileOptions):
        self.options = options

    @exception
    def get_resources(self) -> List[Resource]:
        client = self.options.session.client('iam')
        message_handler("Collecting data from IAM Local Policies...", "HEADER")
        paginator = client.get_paginator('list_policies')
        pages = paginator.paginate(
            Scope='Local'
        )

        resources_found = []
        for policies in pages:
            for data in policies['Policies']:
                resources_found.append(Resource(digest=ResourceDigest(id=data['Arn'], type='aws_iam_policy'),
                                                name=data['PolicyName'],
                                                details='IAM Policy version {}'.format(data['DefaultVersionId']),
                                                group='security'))
        return resources_found


class IAMGROUP(ResourceProvider):

    def __init__(self, options: ProfileOptions):
        self.client = options.session.client('iam')

    @exception
    def get_resources(self) -> List[Resource]:

        message_handler("Collecting data from IAM Groups...", "HEADER")
        paginator = self.client.get_paginator('list_groups')
        pages = paginator.paginate()

        resources_found = []
        for groups in pages:
            for data in groups['Groups']:
                resources_found.append(Resource(digest=ResourceDigest(id=data['GroupName'], type='aws_iam_group'),
                                                name=data['GroupName'],
                                                details='',
                                                group='security'))
        return resources_found
