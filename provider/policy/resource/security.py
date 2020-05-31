from concurrent.futures.thread import ThreadPoolExecutor
from typing import Dict

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
        self.resources_found: List[Resource] = []
        self.relations_found: List[ResourceEdge] = []

    @exception
    def get_resources(self) -> List[Resource]:

        message_handler("Collecting data from IAM Roles...", "HEADER")
        paginator = self.client.get_paginator('list_roles')
        pages = paginator.paginate()

        resources_found = []
        for roles in pages:
            for data in roles['Roles']:
                resource_digest = ResourceDigest(id=data['RoleName'], type='aws_iam_role')
                resources_found.append(Resource(digest=resource_digest,
                                                name=data['RoleName'],
                                                details='',
                                                group='Role'))
                if 'AssumeRolePolicyDocument' in data and 'Statement' in data['AssumeRolePolicyDocument']:
                    for statement in data['AssumeRolePolicyDocument']['Statement']:
                        resources_found.extend(self.analyze_assume_statement(resource_digest, statement))

        self.resources_found = resources_found
        return resources_found

    # TODO: Add support for the following principals:
    # 'cognito-identity.amazonaws.com'
    # 'iot.amazonaws.com'
    # 'quicksight.amazonaws.com'
    # 'glue.amazonaws.com'
    # 'es.amazonaws.com'
    # 'ops.apigateway.amazonaws.com'
    # 'cloud9.amazonaws.com'
    # 'config.amazonaws.com'
    # 'ecs.amazonaws.com'
    # 'eks.amazonaws.com'
    # 'elasticache.amazonaws.com'
    # 'elasticloadbalancing.amazonaws.com'
    # 'elasticmapreduce.amazonaws.com'
    # 'kafka.amazonaws.com'
    # 'organizations.amazonaws.com'
    # 'securityhub.amazonaws.com'
    # 'sso.amazonaws.com'
    # 'support.amazonaws.com'
    # 'trustedadvisor.amazonaws.com'
    # 'appsync.amazonaws.com'
    # 'iotanalytics.amazonaws.com'
    # 'arn:aws:iam::<ACCOUNT_NUMBER>:root'
    # 'ecs-tasks.amazonaws.com'
    # 'firehose.amazonaws.com'
    # 'cognito-idp.amazonaws.com'
    def analyze_assume_statement(self, resource_digest: ResourceDigest, statement) -> List[Resource]:
        resources_found = []
        if 'Principal' in statement and 'Service' in statement['Principal']:
            assuming_services = statement['Principal']['Service']
            if not isinstance(assuming_services, list):
                assuming_services = [assuming_services]
            for assuming_service in assuming_services:
                if assuming_service == 'apigateway.amazonaws.com':
                    service_digest = ResourceDigest(id=assuming_service, type='aws_api_gateway_rest_api')
                    resources_found.append(Resource(
                        digest=service_digest,
                        name="API Gateway",
                        details='',
                        group='AWS Service'))
                    self.relations_found.append(ResourceEdge(from_node=resource_digest, to_node=service_digest))
                elif assuming_service == 'sagemaker.amazonaws.com':
                    service_digest = ResourceDigest(id=assuming_service, type='aws_sagemaker_notebook_instance')
                    resources_found.append(Resource(
                        digest=service_digest,
                        name="Sagemaker",
                        details='',
                        group='AWS Service'))
                    self.relations_found.append(ResourceEdge(from_node=resource_digest, to_node=service_digest))
                elif assuming_service == 'ssm.amazonaws.com':
                    service_digest = ResourceDigest(id=assuming_service, type='aws_ssm_document')
                    resources_found.append(Resource(
                        digest=service_digest,
                        name="SystemsManager",
                        details='',
                        group='AWS Service'))
                    self.relations_found.append(ResourceEdge(from_node=resource_digest, to_node=service_digest))
                elif assuming_service == 'ec2.amazonaws.com':
                    service_digest = ResourceDigest(id=assuming_service, type='aws_instance')
                    resources_found.append(Resource(
                        digest=service_digest,
                        name="EC2",
                        details='',
                        group='AWS Service'))
                    self.relations_found.append(ResourceEdge(from_node=resource_digest, to_node=service_digest))
                elif assuming_service == 'lambda.amazonaws.com':
                    service_digest = ResourceDigest(id=assuming_service, type='aws_lambda_function')
                    resources_found.append(Resource(
                        digest=service_digest,
                        name="Lambda",
                        details='',
                        group='AWS Service'))
                    self.relations_found.append(ResourceEdge(from_node=resource_digest, to_node=service_digest))
        return resources_found

    @exception
    def get_relations(self) -> List[ResourceEdge]:
        additional_relations_found = self.relations_found
        with ThreadPoolExecutor(15) as executor:
            results = executor.map(lambda data: self.analyze_role_relations(data), self.resources_found)
        for result in results:
            additional_relations_found.extend(result)

        return additional_relations_found

    def analyze_role_relations(self, resource: Resource):
        relations_found = []
        if resource.digest.type == 'aws_iam_role':
            response = self.client.list_attached_role_policies(
                RoleName=resource.name
            )
            for policy in response['AttachedPolicies']:
                relations_found.append(ResourceEdge(from_node=resource.digest,
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
