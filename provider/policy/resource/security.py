from concurrent.futures.thread import ThreadPoolExecutor

from provider.policy.command import ProfileOptions
from shared.common import *
from shared.error_handler import exception


class IamPolicy(ResourceProvider):

    def __init__(self, options: ProfileOptions):
        self.options = options

    @exception
    def get_resources(self) -> List[Resource]:
        client = self.options.client('iam')
        message_handler("Collecting data from IAM Policies...", "HEADER")

        resources_found = []

        paginator = client.get_paginator('list_policies')
        pages = paginator.paginate(
            Scope='Local'
        )
        for policies in pages:
            for data in policies['Policies']:
                resources_found.append(self.build_policy(data))

        pages = paginator.paginate(
            Scope='AWS',
            OnlyAttached=True
        )

        for policies in pages:
            for data in policies['Policies']:
                resources_found.append(self.build_policy(data))

        return resources_found

    @staticmethod
    def build_policy(data):
        return Resource(digest=ResourceDigest(id=data['Arn'], type='aws_iam_policy'),
                        name=data['PolicyName'],
                        details='IAM Policy version {}'.format(data['DefaultVersionId']),
                        group='Policy')


class IamGroup(ResourceProvider):

    def __init__(self, options: ProfileOptions):
        self.client = options.client('iam')
        self.resources_found: List[Resource] = []

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
                                                group='Group'))
        self.resources_found = resources_found
        return resources_found

    @exception
    def get_relations(self) -> List[ResourceEdge]:
        relations_found = []
        with ThreadPoolExecutor(15) as executor:
            results = executor.map(lambda resource: self.analyze_relations(resource), self.resources_found)
        for result in results:
            relations_found.extend(result)

        return relations_found

    def analyze_relations(self, resource):
        relations_found = []
        response = self.client.list_attached_group_policies(
            GroupName=resource.name
        )
        for policy in response['AttachedPolicies']:
            relations_found.append(ResourceEdge(from_node=resource.digest,
                                                to_node=ResourceDigest(id=policy['PolicyArn'],
                                                                       type='aws_iam_policy')))
        return relations_found


class IamRole(ResourceProvider):

    def __init__(self, options: ProfileOptions):
        self.client = options.client('iam')
        self.roles_found: List[Resource] = []

    @exception
    def get_resources(self) -> List[Resource]:

        message_handler("Collecting data from IAM Roles...", "HEADER")
        paginator = self.client.get_paginator('list_roles')
        pages = paginator.paginate()

        resources_found = []
        for roles in pages:
            for data in roles['Roles']:
                resources_found.append(Resource(digest=ResourceDigest(id=data['RoleName'], type='aws_iam_role'),
                                                name=data['RoleName'],
                                                details='',
                                                group='Role'))
        self.roles_found = resources_found
        return resources_found

    @exception
    def get_relations(self) -> List[ResourceEdge]:
        resources_found = []
        with ThreadPoolExecutor(15) as executor:
            results = executor.map(lambda data: self.analyze_role_relations(data), self.roles_found)
        for result in results:
            resources_found.extend(result)

        return resources_found

    def analyze_role_relations(self, role):
        relations_found = []
        response = self.client.list_attached_role_policies(
            RoleName=role.name
        )
        for policy in response['AttachedPolicies']:
            relations_found.append(ResourceEdge(from_node=role.digest,
                                                to_node=ResourceDigest(id=policy['PolicyArn'],
                                                                       type='aws_iam_policy')))
        return relations_found


class InstanceProfile(ResourceProvider):

    def __init__(self, vpc_options: ProfileOptions):
        self.vpc_options = vpc_options
        self.relations_found: List[ResourceEdge] = []

    @exception
    def get_resources(self) -> List[Resource]:

        message_handler("Collecting data from Instance Profiles...", "HEADER")
        paginator = self.vpc_options.client('iam').get_paginator('list_instance_profiles')
        pages = paginator.paginate()

        resources_found = []
        relations_found = []
        for groups in pages:
            for data in groups['InstanceProfiles']:
                profile_digest = ResourceDigest(id=data['InstanceProfileName'], type='aws_iam_instance_profile')
                resources_found.append(
                    Resource(digest=profile_digest,
                             name=data['InstanceProfileName'],
                             details='',
                             group='Instance Profile'))
                if len(data['Roles']) == 1:
                    relations_found.append(
                        ResourceEdge(from_node=profile_digest,
                                     to_node=ResourceDigest(id=data['Roles'][0]['RoleName'], type='aws_iam_role')))
        self.relations_found = relations_found
        return resources_found

    @exception
    def get_relations(self) -> List[ResourceEdge]:
        return self.relations_found
