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
                        group='')


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
                                                group=''))
                if 'AssumeRolePolicyDocument' in data and 'Statement' in data['AssumeRolePolicyDocument']:
                    for statement in data['AssumeRolePolicyDocument']['Statement']:
                        resources_found.extend(self.analyze_assume_statement(resource_digest, statement))

        self.resources_found = resources_found
        return resources_found

    def analyze_assume_statement(self, resource_digest: ResourceDigest, statement) -> List[Resource]:
        resources_found = []
        if 'Principal' in statement and 'Service' in statement['Principal']:
            assuming_services = statement['Principal']['Service']
            if not isinstance(assuming_services, list):
                assuming_services = [assuming_services]
            for assuming_service in assuming_services:
                principal_found: Resource = None
                if assuming_service == 'apigateway.amazonaws.com':
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_api_gateway_rest_api'),
                        name="API Gateway",
                        details='',
                        group='')
                elif assuming_service == 'ops.apigateway.amazonaws.com':
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_api_gateway_rest_api'),
                        name="API Gateway ops",
                        details='',
                        group='')
                elif assuming_service == 'sagemaker.amazonaws.com':
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_sagemaker_notebook_instance'),
                        name="Sagemaker",
                        details='',
                        group='')
                elif assuming_service == 'ssm.amazonaws.com':
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_ssm_document'),
                        name="SystemsManager",
                        details='',
                        group='')
                elif assuming_service == 'ec2.amazonaws.com':
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_instance'),
                        name="EC2",
                        details='',
                        group='')
                elif assuming_service == 'lambda.amazonaws.com':
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_lambda_function'),
                        name="Lambda",
                        details='',
                        group='')
                elif assuming_service == 'replicator.lambda.amazonaws.com':
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_lambda_function'),
                        name="Lambda Replicator",
                        details='',
                        group='')
                elif assuming_service == 'edgelambda.lambda.amazonaws.com':
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_lambda_function'),
                        name="Lambda@Edge",
                        details='',
                        group='')
                elif assuming_service == 'ecs.amazonaws.com':
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_ecs_cluster'),
                        name="ECS",
                        details='',
                        group='')
                elif assuming_service == 'ecs-tasks.amazonaws.com':
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_ecs_cluster'),
                        name="ECS Tasks",
                        details='',
                        group='')
                elif assuming_service == 'eks.amazonaws.com':
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_eks_cluster'),
                        name="EKS",
                        details='',
                        group='')
                elif assuming_service == 'es.amazonaws.com':
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_elasticsearch_domain'),
                        name="Elasticsearch Service",
                        details='',
                        group='')
                elif assuming_service == 'es.amazonaws.com':
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_elasticsearch_domain'),
                        name="Elasticsearch Service",
                        details='',
                        group='')
                elif assuming_service == 'cognito-identity.amazonaws.com':
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_cognito_identity_provider'),
                        name="Cognito Identity",
                        details='',
                        group='')
                elif assuming_service == 'cognito-idp.amazonaws.com':
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_cognito_identity_provider'),
                        name="Cognito IdP",
                        details='',
                        group='')
                elif assuming_service == 'email.cognito-idp.amazonaws.com':
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_cognito_identity_provider'),
                        name="Cognito IdP Email",
                        details='',
                        group='')
                elif assuming_service == 'iot.amazonaws.com':
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_iot_thing'),
                        name="Internet of Things",
                        details='',
                        group='')
                elif assuming_service == 'elasticloadbalancing.amazonaws.com':
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_elb'),
                        name="ELB",
                        details='',
                        group='')
                elif assuming_service == 'elasticmapreduce.amazonaws.com':
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_emr'),
                        name="EMR",
                        details='',
                        group='')
                elif assuming_service == 'kafka.amazonaws.com':
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_msk_cluster'),
                        name="MSK",
                        details='',
                        group='')
                elif assuming_service == 'elasticache.amazonaws.com':
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_elasticache_cluster'),
                        name="ElastiCache",
                        details='',
                        group='')
                elif assuming_service == 'appsync.amazonaws.com':
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_appsync_graphql_api'),
                        name="AppSync",
                        details='',
                        group='')
                elif assuming_service == 'iotanalytics.amazonaws.com':
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_iot_analytics'),
                        name="IoT Analytics",
                        details='',
                        group='')
                elif assuming_service == 'securityhub.amazonaws.com':
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_securityhub_account'),
                        name="Security Hub",
                        details='',
                        group='')
                elif assuming_service == 'trustedadvisor.amazonaws.com':
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_trusted_advisor'),
                        name="Trusted Advisor",
                        details='',
                        group='')
                elif assuming_service == 'firehose.amazonaws.com':
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_kinesis_firehose'),
                        name="Kinesis Firehose",
                        details='',
                        group='')
                elif assuming_service == 'glue.amazonaws.com':
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_glue'),
                        name="Glue",
                        details='',
                        group='')
                elif assuming_service == 'quicksight.amazonaws.com':
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_quicksight'),
                        name="QuickSight",
                        details='',
                        group='')
                elif assuming_service == 'cloud9.amazonaws.com':
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_cloud9'),
                        name="Cloud9",
                        details='',
                        group='')
                elif assuming_service == 'organizations.amazonaws.com':
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_organizations_account'),
                        name="Organizations",
                        details='',
                        group='')
                elif assuming_service == 'organizations.amazonaws.com':
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_organizations_account'),
                        name="Organizations",
                        details='',
                        group='')
                elif assuming_service == 'config.amazonaws.com':
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_config'),
                        name="Config",
                        details='',
                        group='')
                elif assuming_service == 'application-autoscaling.amazonaws.com':
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_auto_scaling'),
                        name="Application Autoscaling",
                        details='',
                        group='')
                elif assuming_service == 'autoscaling.amazonaws.com':
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_auto_scaling'),
                        name="Autoscaling",
                        details='',
                        group='')
                elif assuming_service == 'backup.amazonaws.com':
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_backup'),
                        name="Backup",
                        details='',
                        group='')
                elif assuming_service == 'cloudtrail.amazonaws.com':
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_cloudtrail'),
                        name="Cloudtrail",
                        details='',
                        group='')
                elif assuming_service == 'cloudwatch-crossaccount.amazonaws.com':
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_cloudwatch_crossaccount'),
                        name="Cloudwatch Crossaccount",
                        details='',
                        group='')
                elif assuming_service == 'datapipeline.amazonaws.com':
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_data_pipeline'),
                        name="Data Pipeline",
                        details='',
                        group='')
                elif assuming_service == 'dms.amazonaws.com':
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_dms'),
                        name="DMS",
                        details='',
                        group='')
                elif assuming_service == 'dynamodb.application-autoscaling.amazonaws.com':
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_auto_scaling'),
                        name="DynamoDB Application Autoscaling",
                        details='',
                        group='')
                elif assuming_service == 'elasticbeanstalk.amazonaws.com':
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_elastic_beanstalk_environment'),
                        name="Elastic Beanstalk",
                        details='',
                        group='')
                elif assuming_service == 'fms.amazonaws.com':
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_fms'),
                        name="Firewall Manager",
                        details='',
                        group='')
                elif assuming_service == 'globalaccelerator.amazonaws.com':
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_global_accelerator'),
                        name="Global Accelerator",
                        details='',
                        group='')
                elif assuming_service == 'inspector.amazonaws.com':
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_inspector'),
                        name="inspector",
                        details='',
                        group='')
                elif assuming_service == 'logger.cloudfront.amazonaws.com':
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_cloudfront_distribution'),
                        name="CloudFront Logger",
                        details='',
                        group='')
                elif assuming_service == 'migrationhub.amazonaws.com':
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_migration_hub'),
                        name="Migration Hub",
                        details='',
                        group='')
                elif assuming_service == 'rds.amazonaws.com':
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_db_instance'),
                        name="RDS",
                        details='',
                        group='')
                elif assuming_service == 'sns.amazonaws.com':
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_sns_topic'),
                        name="SNS",
                        details='',
                        group='')
                else:
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type='aws_general'),
                        name=assuming_service,
                        details='',
                        group='')
                if principal_found is not None:
                    resources_found.append(principal_found)
                    self.create_principal_relation(resource_digest, principal_found.digest)
        return resources_found

    def create_principal_relation(self, resource_digest, service_digest):
        self.relations_found.append(ResourceEdge(from_node=resource_digest, to_node=service_digest, label='assumed by'))

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
                             group=''))
                if len(data['Roles']) == 1:
                    relations_found.append(
                        ResourceEdge(from_node=profile_digest,
                                     to_node=ResourceDigest(id=data['Roles'][0]['RoleName'], type='aws_iam_role')))
        self.relations_found = relations_found
        return resources_found

    @exception
    def get_relations(self) -> List[ResourceEdge]:
        return self.relations_found
