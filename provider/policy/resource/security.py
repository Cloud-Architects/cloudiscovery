from concurrent.futures.thread import ThreadPoolExecutor
from typing import List

from shared.common import BaseOptions
from shared.common import (
    ResourceProvider,
    Resource,
    message_handler,
    ResourceDigest,
    ResourceEdge,
)
from shared.error_handler import exception


class Principals:

    principals = dict()
    principals = {
                "apigateway.amazonaws.com": {"type": "aws_api_gateway_rest_api", "name": "API Gateway"},
                "ops.apigateway.amazonaws.com": {"type": "aws_api_gateway_rest_api", "name": "API Gateway"},
                "sagemaker.amazonaws.com": {"type": "aws_sagemaker_notebook_instance", "name": "Sagemaker"},
                "ssm.amazonaws.com": {"type": "aws_ssm_document", "name": "SystemsManager"},
                "ec2.amazonaws.com": {"type": "aws_instance", "name": "EC2"},
                "lambda.amazonaws.com": {"type": "aws_lambda_function", "name": "Lambda"},
                "replicator.lambda.amazonaws.com": {"type": "aws_lambda_function", "name": "Lambda Replicator"},
                "edgelambda.lambda.amazonaws.com": {"type": "aws_lambda_function", "name": "Lambda@Edge"},
                "ecs.amazonaws.com": {"type": "aws_ecs_cluster", "name": "ECS"},
                "ecs-tasks.amazonaws.com": {"type": "aws_ecs_cluster", "name": "ECS Tasks"},
                "eks.amazonaws.com": {"type": "aws_eks_cluster", "name": "EKS"},
                "es.amazonaws.com": {"type": "aws_elasticsearch_domain", "name": "Elasticsearch Service"},
                "cognito-identity.amazonaws.com": {"type": "aws_cognito_identity_provider", "name": "Cognito Identity"},
                "cognito-idp.amazonaws.com": {"type": "aws_cognito_identity_provider", "name": "Cognito IdP"},
                "email.cognito-idp.amazonaws.com": {"type": "aws_cognito_identity_provider", "name": "Cognito IdP Email"},
                "iot.amazonaws.com": {"type": "aws_iot_thing", "name": "Internet of Things"},
                "elasticloadbalancing.amazonaws.com": {"type": "aws_elb", "name": "ELB"},
                "elasticmapreduce.amazonaws.com": {"type": "aws_emr", "name": "EMR"},
                "kafka.amazonaws.com": {"type": "aws_msk_cluster", "name": "MSK"},
                "elasticache.amazonaws.com": {"type": "aws_elasticache_cluster", "name": "ElastiCache"},
                "appsync.amazonaws.com": {"type": "aws_appsync_graphql_api", "name": "AppSync"},
                "iotanalytics.amazonaws.com": {"type": "aws_iot_analytics", "name": "IoT Analytics"},
                "securityhub.amazonaws.com": {"type": "aws_securityhub_account", "name": "Security Hub"},
                "trustedadvisor.amazonaws.com": {"type": "aws_trusted_advisor", "name": "Trusted Advisor"},
                "firehose.amazonaws.com": {"type": "aws_kinesis_firehose", "name": "Kinesis Firehose"},
                "glue.amazonaws.com": {"type": "aws_glue", "name": "Glue"},
                "quicksight.amazonaws.com": {"type": "aws_quicksight", "name": "QuickSight"},
                "cloud9.amazonaws.com": {"type": "aws_cloud9", "name": "Cloud9"},
                "organizations.amazonaws.com": {"type": "aws_organizations_account", "name": "Organizations"},
                "config.amazonaws.com": {"type": "aws_config", "name": "Config"},
                "application-autoscaling.amazonaws.com": {"type": "aws_auto_scaling", "name": "Application Autoscaling"},
                "autoscaling.amazonaws.com": {"type": "aws_auto_scaling", "name": "Autoscaling"},
                "backup.amazonaws.com": {"type": "aws_backup", "name": "Backup"},
                "cloudtrail.amazonaws.com": {"type": "aws_cloudtrail", "name": "Cloudtrail"},
                "cloudwatch-crossaccount.amazonaws.com": {"type": "aws_cloudwatch_crossaccount", "name": "Cloudwatch Crossaccount"},
                "datapipeline.amazonaws.com": {"type": "aws_data_pipeline", "name": "Data Pipeline"},
                "dms.amazonaws.com": {"type": "aws_dms", "name": "DMS"},
                "dynamodb.application-autoscaling.amazonaws.com": {"type": "aws_auto_scaling", "name": "DynamoDB Application Autoscaling"},
                "elasticbeanstalk.amazonaws.com": {"type": "aws_elastic_beanstalk_environment", "name": "Elastic Beanstalk"},
                "fms.amazonaws.com": {"type": "aws_fms", "name": "Firewall Manager"},
                "globalaccelerator.amazonaws.com": {"type": "aws_global_accelerator", "name": "Global Accelerator"},
                "inspector.amazonaws.com": {"type": "aws_inspector", "name": "inspector"},
                "logger.cloudfront.amazonaws.com": {"type": "aws_cloudfront_distribution", "name": "CloudFront Logger"},
                "migrationhub.amazonaws.com": {"type": "aws_migration_hub", "name": "Migration Hub"},
                "rds.amazonaws.com": {"type": "aws_db_instance", "name": "RDS"},
                "sns.amazonaws.com": {"type": "aws_sns_topic", "name": "SNS"}}


class IamPolicy(ResourceProvider):
    def __init__(self, options: BaseOptions):
        super().__init__()
        self.options = options

    @exception
    def get_resources(self) -> List[Resource]:
        client = self.options.client("iam")
        message_handler("Collecting data from IAM Policies...", "HEADER")

        resources_found = []

        paginator = client.get_paginator("list_policies")
        pages = paginator.paginate(Scope="Local")
        for policies in pages:
            for data in policies["Policies"]:
                resources_found.append(self.build_policy(data))

        pages = paginator.paginate(Scope="AWS", OnlyAttached=True)

        for policies in pages:
            for data in policies["Policies"]:
                resources_found.append(self.build_policy(data))

        return resources_found

    @staticmethod
    def build_policy(data):
        return Resource(
            digest=ResourceDigest(id=data["Arn"], type="aws_iam_policy"),
            name=data["PolicyName"],
            details="IAM Policy version {}".format(data["DefaultVersionId"]),
            group="",
        )


class IamGroup(ResourceProvider):
    def __init__(self, options: BaseOptions):
        super().__init__()
        self.client = options.client("iam")
        self.resources_found: List[Resource] = []

    @exception
    def get_resources(self) -> List[Resource]:

        message_handler("Collecting data from IAM Groups...", "HEADER")
        paginator = self.client.get_paginator("list_groups")
        pages = paginator.paginate()

        resources_found = []
        for groups in pages:
            for data in groups["Groups"]:
                resources_found.append(
                    Resource(
                        digest=ResourceDigest(
                            id=data["GroupName"], type="aws_iam_group"
                        ),
                        name=data["GroupName"],
                        details="",
                        group="Group",
                    )
                )
        self.resources_found = resources_found
        return resources_found

    @exception
    def get_relations(self) -> List[ResourceEdge]:
        relations_found = []
        with ThreadPoolExecutor(15) as executor:
            results = executor.map(
                lambda resource: self.analyze_relations(resource), self.resources_found
            )
        for result in results:
            relations_found.extend(result)

        return relations_found

    def analyze_relations(self, resource):
        relations_found = []
        response = self.client.list_attached_group_policies(GroupName=resource.name)
        for policy in response["AttachedPolicies"]:
            relations_found.append(
                ResourceEdge(
                    from_node=resource.digest,
                    to_node=ResourceDigest(
                        id=policy["PolicyArn"], type="aws_iam_policy"
                    ),
                )
            )
        return relations_found


class IamRole(ResourceProvider):
    def __init__(self, options: BaseOptions):
        super().__init__()
        self.client = options.client("iam")
        self.resources_found: List[Resource] = []

    @exception
    def get_resources(self) -> List[Resource]:

        message_handler("Collecting data from IAM Roles...", "HEADER")
        paginator = self.client.get_paginator("list_roles")
        pages = paginator.paginate()

        resources_found = []
        for roles in pages:
            for data in roles["Roles"]:
                resource_digest = ResourceDigest(
                    id=data["RoleName"], type="aws_iam_role"
                )
                resources_found.append(
                    Resource(
                        digest=resource_digest,
                        name=data["RoleName"],
                        details="",
                        group="",
                    )
                )
                if (
                    "AssumeRolePolicyDocument" in data
                    and "Statement" in data["AssumeRolePolicyDocument"]
                ):
                    for statement in data["AssumeRolePolicyDocument"]["Statement"]:
                        resources_found.extend(
                            self.analyze_assume_statement(resource_digest, statement)
                        )

        self.resources_found = resources_found
        return resources_found

    def analyze_assume_statement(
        self, resource_digest: ResourceDigest, statement
    ) -> List[Resource]:
        resources_found = []
        if "Principal" in statement and "Service" in statement["Principal"]:
            assuming_services = statement["Principal"]["Service"]
            if not isinstance(assuming_services, list):
                assuming_services = [assuming_services]
            for assuming_service in assuming_services:
                principal_found: Resource = None
                if assuming_service in Principals.principals:
                    principal_found = Resource(
                        digest=ResourceDigest(
                            id=assuming_service, type=Principals.principals[assuming_service]["type"]
                        ),
                        name=Principals.principals[assuming_service]["name"],
                        details="",
                        group="",
                    )
                else:
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type="aws_general"),
                        name=assuming_service,
                        details="",
                        group="",
                    )
                if principal_found is not None:
                    resources_found.append(principal_found)
                    self.create_principal_relation(
                        resource_digest, principal_found.digest
                    )
        return resources_found

    def create_principal_relation(self, resource_digest, service_digest):
        self.relations_found.append(
            ResourceEdge(
                from_node=resource_digest, to_node=service_digest, label="assumed by"
            )
        )

    @exception
    def get_relations(self) -> List[ResourceEdge]:
        additional_relations_found = self.relations_found
        with ThreadPoolExecutor(15) as executor:
            results = executor.map(
                lambda data: self.analyze_role_relations(data), self.resources_found
            )
        for result in results:
            additional_relations_found.extend(result)

        return additional_relations_found

    def analyze_role_relations(self, resource: Resource):
        relations_found = []
        if resource.digest.type == "aws_iam_role":
            response = self.client.list_attached_role_policies(RoleName=resource.name)
            for policy in response["AttachedPolicies"]:
                relations_found.append(
                    ResourceEdge(
                        from_node=resource.digest,
                        to_node=ResourceDigest(
                            id=policy["PolicyArn"], type="aws_iam_policy"
                        ),
                    )
                )
        return relations_found


class InstanceProfile(ResourceProvider):
    def __init__(self, vpc_options: BaseOptions):
        super().__init__()
        self.vpc_options = vpc_options

    @exception
    def get_resources(self) -> List[Resource]:

        message_handler("Collecting data from Instance Profiles...", "HEADER")
        paginator = self.vpc_options.client("iam").get_paginator(
            "list_instance_profiles"
        )
        pages = paginator.paginate()

        resources_found = []
        relations_found = []
        for groups in pages:
            for data in groups["InstanceProfiles"]:
                profile_digest = ResourceDigest(
                    id=data["InstanceProfileName"], type="aws_iam_instance_profile"
                )
                resources_found.append(
                    Resource(
                        digest=profile_digest,
                        name=data["InstanceProfileName"],
                        details="",
                        group="",
                    )
                )
                if len(data["Roles"]) == 1:
                    relations_found.append(
                        ResourceEdge(
                            from_node=profile_digest,
                            to_node=ResourceDigest(
                                id=data["Roles"][0]["RoleName"], type="aws_iam_role"
                            ),
                        )
                    )
        self.relations_found = relations_found
        return resources_found
