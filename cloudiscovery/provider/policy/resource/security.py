from concurrent.futures.thread import ThreadPoolExecutor
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


class Principals:
    # Source: https://gist.github.com/shortjared/4c1e3fe52bdfa47522cfe5b41e5d6f22
    principals = {
        "a4b.amazonaws.com": {
            "type": "aws_alexa_for_business",
            "name": "Alexa for Business",
            "group": "business",
        },
        "acm-pca.amazonaws.com": {
            "type": "aws_acm",
            "name": "ACM PCA",
            "group": "security",
        },
        "acm.amazonaws.com": {"type": "aws_acm", "name": "ACM", "group": "security"},
        "alexa-appkit": {
            "type": "aws_alexa_skill",
            "name": "Alexa App kti",
            "group": "business",
        },
        "alexa-connectedhome": {
            "type": "aws_alexa",
            "name": "Alexa Connected Home",
            "group": "business",
        },
        "amazonmq": {"type": "aws_mq", "name": "MQ", "group": "integration"},
        "apigateway.amazonaws.com": {
            "type": "aws_api_gateway_rest_api",
            "name": "API Gateway",
            "group": "network",
        },
        "application-autoscaling.amazonaws.com": {
            "type": "aws_auto_scaling",
            "name": "Application Autoscaling",
            "group": "network",
        },
        "appstream.application-autoscaling.amazonaws.com": {
            "type": "aws_auto_scaling",
            "name": "Appstream Autoscaling",
            "group": "network",
        },
        "appsync.amazonaws.com": {
            "type": "aws_appsync_graphql_api",
            "name": "AppSync",
            "group": "integration",
        },
        "athena.amazonaws.com": {
            "type": "aws_athena",
            "name": "Athena",
            "group": "analytics",
        },
        "autoscaling.amazonaws.com": {
            "type": "aws_auto_scaling",
            "name": "Autoscaling",
            "group": "network",
        },
        "aws-artifact-account-sync.amazonaws": {
            "type": "aws_artifact",
            "name": "Artifact",
            "group": "security",
        },
        "backup.amazonaws.com": {
            "type": "aws_backup",
            "name": "Backup",
            "group": "storage",
        },
        "batch.amazonaws.com": {
            "type": "aws_batch",
            "name": "Batch",
            "group": "compute",
        },
        "billingconsole.amazonaws.com": {
            "type": "aws_billingconsole",
            "name": "Billing Console",
            "group": "general",
        },
        "ce.amazonaws.com": {
            "type": "aws_ce",
            "name": "Cost Explorer",
            "group": "general",
        },
        "channels.lex.amazonaws.com": {
            "type": "aws_lex",
            "name": "Lex Channels",
            "group": "general",
        },
        "chime.amazonaws.com": {
            "type": "aws_chime",
            "name": "Chime",
            "group": "general",
        },
        "cloud9.amazonaws.com": {
            "type": "aws_cloud9",
            "name": "Cloud9",
            "group": "devtools",
        },
        "clouddirectory.amazonaws.com": {
            "type": "aws_clouddirectory",
            "name": "Cloud Directory",
            "group": "security",
        },
        "cloudformation.amazonaws.com": {
            "type": "aws_cloudformation",
            "name": "CloudFormation",
            "group": "management",
        },
        "cloudfront.amazonaws.com": {
            "type": "aws_cloudfront_distribution",
            "name": "CloudFront",
            "group": "network",
        },
        "cloudhsm.amazonaws.com": {
            "type": "aws_cloudhsm",
            "name": "CloudHSM",
            "group": "security",
        },
        "cloudsearch.amazonaws.com": {
            "type": "aws_cloudsearch",
            "name": "CloudSearch",
            "group": "analytics",
        },
        "cloudtrail.amazonaws.com": {
            "type": "aws_cloudtrail",
            "name": "Cloudtrail",
            "group": "management",
        },
        "codebuild.amazonaws.com": {
            "type": "aws_codebuild",
            "name": "CodeBuild",
            "group": "devtools",
        },
        "codecommit.amazonaws.com": {
            "type": "aws_codecommit",
            "name": "CodeCommit",
            "group": "devtools",
        },
        "codedeploy.${AWS::Region}.amazonaws.com": {
            "type": "aws_codedeploy",
            "name": "CodeDeploy",
            "group": "devtools",
        },
        "codedeploy.amazonaws.com": {
            "type": "aws_codedeploy",
            "name": "CodeDeploy",
            "group": "devtools",
        },
        "codepipeline.amazonaws.com": {
            "type": "aws_codepipeline",
            "name": "CodePipeline",
            "group": "devtools",
        },
        "codestar.amazonaws.com": {
            "type": "aws_codestar",
            "name": "CodeStar",
            "group": "devtools",
        },
        "cognito-identity.amazonaws.com": {
            "type": "aws_cognito_identity_provider",
            "name": "Cognito Identity",
            "group": "security",
        },
        "cognito-idp.amazonaws.com": {
            "type": "aws_cognito_identity_provider",
            "name": "Cognito IdP",
            "group": "security",
        },
        "cognito-sync.amazonaws.com": {
            "type": "aws_cognito_identity_provider",
            "name": "Cognito Sync",
            "group": "security",
        },
        "config-multiaccountsetup.amazonaws.com": {
            "type": "aws_config",
            "name": "Config",
            "group": "management",
        },
        "config.amazonaws.com": {
            "type": "aws_config",
            "name": "Config",
            "group": "management",
        },
        "continuousexport.discovery.amazonaws.com": {
            "type": "aws_discovery",
            "name": "Discovery",
            "group": "migration",
        },
        "custom-resource.application-autoscaling.amazonaws.com": {
            "type": "aws_auto_scaling",
            "name": "Custom Autoscaling",
            "group": "network",
        },
        "datapipeline.amazonaws.com": {
            "type": "aws_data_pipeline",
            "name": "Data Pipeline",
            "group": "analytics",
        },
        "dax.amazonaws.com": {
            "type": "aws_dax",
            "name": "DynamoDB DAX",
            "group": "database",
        },
        "deeplens.amazonaws.com": {
            "type": "aws_deeplens",
            "name": "Deep Lens",
            "group": "database",
        },
        "delivery.logs.amazonaws.com": {
            "type": "aws_delivery_logs",
            "name": "Delivery Logs",
            "group": "general",
        },
        "diode.amazonaws.com": {
            "type": "aws_diode",
            "name": "Diode",
            "group": "general",
        },
        "directconnect.amazonaws.com": {
            "type": "aws_directconnect",
            "name": "Direct Connect",
            "group": "network",
        },
        "discovery.amazonaws.com": {
            "type": "aws_discovery",
            "name": "Discovery",
            "group": "migration",
        },
        "dlm.amazonaws.com": {"type": "aws_dlm", "name": "DLM", "group": "migration"},
        "dms.amazonaws.com": {"type": "aws_dms", "name": "DMS", "group": "database"},
        "ds.amazonaws.com": {
            "type": "aws_ds",
            "name": "DirectoryService",
            "group": "security",
        },
        "dynamodb.amazonaws.com": {
            "type": "aws_dynamodb",
            "name": "DynamoDB",
            "group": "database",
        },
        "dynamodb.application-autoscaling.amazonaws.com": {
            "type": "aws_auto_scaling",
            "name": "DynamoDB Application Autoscaling",
            "group": "network",
        },
        "ec2.amazonaws.com": {
            "type": "aws_instance",
            "name": "EC2",
            "group": "compute",
        },
        "ec2.application-autoscaling.amazonaws.com": {
            "type": "aws_auto_scaling",
            "name": "EC2 Application Autoscaling",
            "group": "network",
        },
        "ec2fleet.amazonaws.com": {
            "type": "aws_instance",
            "name": "EC2 Fleet",
            "group": "compute",
        },
        "ec2scheduled.amazonaws.com": {
            "type": "aws_instance",
            "name": "EC2 Fleet",
            "group": "compute",
        },
        "ecr.amazonaws.com": {"type": "aws_ecr", "name": "ECR", "group": "compute"},
        "ecs.amazonaws.com": {
            "type": "aws_ecs_cluster",
            "name": "ECS",
            "group": "compute",
        },
        "ecs-tasks.amazonaws.com": {
            "type": "aws_ecs_cluster",
            "name": "ECS Tasks",
            "group": "compute",
        },
        "ecs.application-autoscaling.amazonaws.com": {
            "type": "aws_auto_scaling",
            "name": "ECS Application Autoscaling",
            "group": "network",
        },
        "edgelambda.amazonaws.com": {
            "type": "aws_lambda_function",
            "name": "Lambda@Edge",
            "group": "compute",
        },
        "eks.amazonaws.com": {
            "type": "aws_eks_cluster",
            "name": "EKS",
            "group": "compute",
        },
        "elasticache.amazonaws.com": {
            "type": "aws_elasticache_cluster",
            "name": "ElastiCache",
            "group": "database",
        },
        "elasticbeanstalk.amazonaws.com": {
            "type": "aws_elastic_beanstalk_environment",
            "name": "Elastic Beanstalk",
            "group": "compute",
        },
        "elasticfilesystem.amazonaws.com": {
            "type": "aws_efs",
            "name": "EFS",
            "group": "storage",
        },
        "elasticloadbalancing.amazonaws.com": {
            "type": "aws_elb",
            "name": "ELB",
            "group": "network",
        },
        "elasticmapreduce.amazonaws.com": {
            "type": "aws_emr",
            "name": "EMR",
            "group": "analytics",
        },
        "elastictranscoder.amazonaws.com": {
            "type": "aws_elastictranscoder",
            "name": "ElasticTranscoder",
            "group": "media",
        },
        "es.amazonaws.com": {
            "type": "aws_elasticsearch_domain",
            "name": "Elasticsearch Service",
            "group": "analytics",
        },
        "events.amazonaws.com": {
            "type": "aws_events",
            "name": "Event Bridge",
            "group": "integration",
        },
        "firehose.amazonaws.com": {
            "type": "aws_kinesis_firehose",
            "name": "Kinesis Firehose",
            "group": "analytics",
        },
        "fms.amazonaws.com": {
            "type": "aws_fms",
            "name": "Firewall Manager",
            "group": "security",
        },
        "freertos.amazonaws.com": {
            "type": "aws_freertos",
            "name": "FreeRTOS",
            "group": "iot",
        },
        "fsx.amazonaws.com": {"type": "aws_fsx", "name": "FSx", "group": "storage"},
        "gamelift.amazonaws.com": {
            "type": "aws_gamelift",
            "name": "Gamelift",
            "group": "game",
        },
        "glacier.amazonaws.com": {
            "type": "aws_glacier",
            "name": "Glacier",
            "group": "storage",
        },
        "glue.amazonaws.com": {
            "type": "aws_glue",
            "name": "Glue",
            "group": "analytics",
        },
        "greengrass.amazonaws.com": {
            "type": "aws_greengrass",
            "name": "Greengrass",
            "group": "iot",
        },
        "guardduty.amazonaws.com": {
            "type": "aws_guardduty",
            "name": "GuardDuty",
            "group": "security",
        },
        "health.amazonaws.com": {
            "type": "aws_health",
            "name": "health",
            "group": "general",
        },
        "iam.amazonaws.com": {"type": "aws_iam", "name": "IAM", "group": "security"},
        "importexport.amazonaws.com": {
            "type": "aws_importexport",
            "name": "Import Export",
            "group": "security",
        },
        "inspector.amazonaws.com": {
            "type": "aws_inspector",
            "name": "inspector",
            "group": "security",
        },
        "iot.amazonaws.com": {
            "type": "aws_iot_thing",
            "name": "Internet of Things",
            "group": "iot",
        },
        "iotanalytics.amazonaws.com": {
            "type": "aws_iot_analytics",
            "name": "IoT Analytics",
            "group": "iot",
        },
        "iotthingsgraph.amazonaws.com": {
            "type": "aws_iot_analytics",
            "name": "IoT Graph",
            "group": "iot",
        },
        "jellyfish.amazonaws.com": {
            "type": "aws_jellyfish",
            "name": "Jellyfish",
            "group": "general",
        },
        "kinesis.amazonaws.com": {
            "type": "aws_kinesis",
            "name": "Kinesis",
            "group": "analytics",
        },
        "kinesisanalytics.amazonaws.com": {
            "type": "aws_kinesisanalytics",
            "name": "Kinesis Analytics",
            "group": "analytics",
        },
        "kms.amazonaws.com": {"type": "aws_kms", "name": "KMS", "group": "security"},
        "lakeformation.amazonaws.com": {
            "type": "aws_lakeformation",
            "name": "Lake Formation",
            "group": "analytics",
        },
        "lambda.amazonaws.com": {
            "type": "aws_lambda_function",
            "name": "Lambda",
            "group": "compute",
        },
        "lex.amazonaws.com": {"type": "aws_lex", "name": "Lex", "group": "general"},
        "license-manager.amazonaws.com": {
            "type": "aws_license_manager",
            "name": "License Manager",
            "group": "management",
        },
        "lightsail.amazonaws.com": {
            "type": "aws_lightsail",
            "name": "Lightsail",
            "group": "compute",
        },
        "logs.amazonaws.com": {"type": "aws_logs", "name": "Logs", "group": "general"},
        "machinelearning.amazonaws.com": {
            "type": "aws_machinelearning",
            "name": "Machine Learning",
            "group": "ml",
        },
        "macie.amazonaws.com": {
            "type": "aws_macie",
            "name": "Macie",
            "group": "security",
        },
        "managedservices.amazonaws.com": {
            "type": "aws_managedservices",
            "name": "Managed Services",
            "group": "general",
        },
        "mediaconnect.amazonaws.com": {
            "type": "aws_media_connect",
            "name": "Media Connect",
            "group": "media",
        },
        "mediaconvert.amazonaws.com": {
            "type": "aws_media_convert",
            "name": "Media Convert",
            "group": "media",
        },
        "mediapackage.amazonaws.com": {
            "type": "aws_media_package",
            "name": "Media Package",
            "group": "media",
        },
        "mediastore.amazonaws.com": {
            "type": "aws_media_store",
            "name": "Media Store",
            "group": "media",
        },
        "mediatailor.amazonaws.com": {
            "type": "aws_media_tailor",
            "name": "Media Tailor",
            "group": "media",
        },
        "metering-marketplace.amazonaws.com": {
            "type": "aws_marketplace",
            "name": "Metering Marketplace",
            "group": "general",
        },
        "migrationhub.amazonaws.com": {
            "type": "aws_migration_hub",
            "name": "Migration Hub",
            "group": "migration",
        },
        "mobilehub.amazonaws.com": {
            "type": "aws_mobile_hub",
            "name": "Mobile Hub",
            "group": "general",
        },
        "monitoring.amazonaws.com": {
            "type": "aws_monitoring",
            "name": "Monitoring",
            "group": "general",
        },
        "monitoring.rds.amazonaws.com": {
            "type": "aws_db_instance",
            "name": "RDS Monitoring",
            "group": "database",
        },
        "opsworks-cm.amazonaws.com": {
            "type": "aws_opsworks",
            "name": "Opswork CM",
            "group": "management",
        },
        "opsworks.amazonaws.com": {
            "type": "aws_opsworks",
            "name": "Opswork",
            "group": "management",
        },
        "organizations.amazonaws.com": {
            "type": "aws_organizations_account",
            "name": "Organizations",
            "group": "management",
        },
        "pinpoint.amazonaws.com": {
            "type": "aws_pinpoint",
            "name": "Pinpoint",
            "group": "engagement",
        },
        "polly.amazonaws.com": {"type": "aws_polly", "name": "Polly", "group": "ml"},
        "qldb.amazonaws.com": {
            "type": "aws_qldb",
            "name": "QLDB",
            "group": "database",
        },
        "quicksight.amazonaws.com": {
            "type": "aws_quicksight",
            "name": "QuickSight",
            "group": "analytics",
        },
        "ram.amazonaws.com": {
            "type": "aws_ram",
            "name": "Resource Access Manager",
            "group": "security",
        },
        "rds.amazonaws.com": {
            "type": "aws_db_instance",
            "name": "RDS",
            "group": "database",
        },
        "redshift.amazonaws.com": {
            "type": "aws_redshift",
            "name": "Redshift",
            "group": "database",
        },
        "rekognition.amazonaws.com": {
            "type": "aws_rekognition",
            "name": "Rekognition",
            "group": "ml",
        },
        "replication.dynamodb.amazonaws.com": {
            "type": "aws_dynamodb",
            "name": "DynamoDB Replication",
            "group": "database",
        },
        "resource-groups.amazonaws.com": {
            "type": "aws_resource_groups",
            "name": "Resource Groups",
            "group": "management",
        },
        "robomaker.amazonaws.com": {
            "type": "aws_robomaker",
            "name": "Resource Groups",
            "group": "robotics",
        },
        "route53.amazonaws.com": {
            "type": "aws_route53",
            "name": "Route53",
            "group": "network",
        },
        "route53domains.amazonaws.com": {
            "type": "aws_route53",
            "name": "Route53 Domains",
            "group": "network",
        },
        "route53resolver.amazonaws.com": {
            "type": "aws_route53",
            "name": "Route53 Resolver",
            "group": "network",
        },
        "s3.amazonaws.com": {"type": "aws_s3", "name": "S3", "group": "storage"},
        "sagemaker.amazonaws.com": {
            "type": "aws_sagemaker",
            "name": "Sagemaker",
            "group": "ml",
        },
        "secretsmanager.amazonaws.com": {
            "type": "aws_secretsmanager",
            "name": "Secrets Manager",
            "group": "security",
        },
        "serverlessrepo.amazonaws.com": {
            "type": "aws_serverlessrepo",
            "name": "Serverless Application Repository",
            "group": "compute",
        },
        "servicecatalog.amazonaws.com": {
            "type": "aws_servicecatalog",
            "name": "Service Catalog",
            "group": "management",
        },
        "servicediscovery.amazonaws.com": {
            "type": "aws_servicediscovery",
            "name": "Service Discovery",
            "group": "management",
        },
        "ses.amazonaws.com": {"type": "aws_ses", "name": "SES", "group": "engagement"},
        "shield.amazonaws.com": {
            "type": "aws_shield",
            "name": "Shield",
            "group": "security",
        },
        "signer.amazonaws.com": {
            "type": "aws_signer",
            "name": "Signer",
            "group": "security",
        },
        "signin.amazonaws.com": {
            "type": "aws_signin",
            "name": "Signin",
            "group": "security",
        },
        "sms.amazonaws.com": {
            "type": "aws_sms",
            "name": "Server Migration Service",
            "group": "migration",
        },
        "sns.amazonaws.com": {
            "type": "aws_sns_topic",
            "name": "SNS",
            "group": "integration",
        },
        "spotfleet.amazonaws.com": {
            "type": "aws_spotfleet",
            "name": "Spot Fleet",
            "group": "compute",
        },
        "sqs.amazonaws.com": {
            "type": "aws_sqs",
            "name": "SQS",
            "group": "integration",
        },
        "ssm.amazonaws.com": {
            "type": "aws_ssm_document",
            "name": "SystemsManager",
            "group": "management",
        },
        "sso.amazonaws.com": {"type": "aws_sso", "name": "SSO", "group": "security"},
        "states.amazonaws.com": {
            "type": "aws_states",
            "name": "States",
            "group": "general",
        },
        "storagegateway.amazonaws.com": {
            "type": "aws_storagegateway",
            "name": "Storage Gateway",
            "group": "storage",
        },
        "sts.amazonaws.com": {"type": "aws_sts", "name": "STS", "group": "security"},
        "support.amazonaws.com": {
            "type": "aws_support",
            "name": "Support",
            "group": "general",
        },
        "swf.amazonaws.com": {"type": "aws_swf", "name": "SWF", "group": "general"},
        "tagging.amazonaws.com": {
            "type": "aws_tagging",
            "name": "Tagging",
            "group": "general",
        },
        "tagpolicies.tag.amazonaws.com": {
            "type": "aws_tagging",
            "name": "Tagging",
            "group": "general",
        },
        "transfer.amazonaws.com": {
            "type": "aws_transfer",
            "name": "Transfer",
            "group": "migration",
        },
        "translate.amazonaws.com": {
            "type": "aws_translate",
            "name": "Translate",
            "group": "ml",
        },
        "trustedadvisor.amazonaws.com": {
            "type": "aws_trusted_advisor",
            "name": "Trusted Advisor",
            "group": "management",
        },
        "tts.amazonaws.com": {
            "type": "aws_tts",
            "name": "Trusted Advisor",
            "group": "management",
        },
        "vmie.amazonaws.com": {
            "type": "aws_vmie",
            "name": "Import Export",
            "group": "migration",
        },
        "waf-regional.amazonaws.com": {
            "type": "aws_waf",
            "name": "WAF Regional",
            "group": "security",
        },
        "waf.amazonaws.com": {
            "type": "aws_waf",
            "name": "WAF Regional",
            "group": "security",
        },
        "workdocs.amazonaws.com": {
            "type": "aws_workdocs",
            "name": "WorkDocs",
            "group": "business",
        },
        "worklink.amazonaws.com": {
            "type": "aws_worklink",
            "name": "WorkLink",
            "group": "business",
        },
        "workmail.amazonaws.com": {
            "type": "aws_workmail",
            "name": "WorkMail",
            "group": "business",
        },
        "workspaces.amazonaws.com": {
            "type": "aws_workspaces",
            "name": "WorkSpaces",
            "group": "business",
        },
        "xray.amazonaws.com": {
            "type": "aws_xray",
            "name": "X-Ray",
            "group": "devtools",
        },
        "ops.apigateway.amazonaws.com": {
            "type": "aws_api_gateway_rest_api",
            "name": "API Gateway",
            "group": "network",
        },
        "replicator.lambda.amazonaws.com": {
            "type": "aws_lambda_function",
            "name": "Lambda Replicator",
            "group": "compute",
        },
        "email.cognito-idp.amazonaws.com": {
            "type": "aws_cognito_identity_provider",
            "name": "Cognito IdP Email",
            "group": "security",
        },
        "kafka.amazonaws.com": {
            "type": "aws_msk_cluster",
            "name": "MSK",
            "group": "analytics",
        },
        "securityhub.amazonaws.com": {
            "type": "aws_securityhub_account",
            "name": "Security Hub",
            "group": "security",
        },
        "cloudwatch-crossaccount.amazonaws.com": {
            "type": "aws_cloudwatch_crossaccount",
            "name": "Cloudwatch Crossaccount",
            "group": "management",
        },
        "globalaccelerator.amazonaws.com": {
            "type": "aws_global_accelerator",
            "name": "Global Accelerator",
            "group": "network",
        },
        "logger.cloudfront.amazonaws.com": {
            "type": "aws_cloudfront_distribution",
            "name": "CloudFront Logger",
            "group": "network",
        },
        "connect.amazonaws.com": {
            "type": "aws_connect",
            "name": "Connect",
            "group": "engagement",
        },
        "config-conforms.amazonaws.com": {
            "type": "aws_config",
            "name": "Config Conforms",
            "group": "management",
        },
        "iotsitewise.amazonaws.com": {
            "type": "aws_iotsitewise",
            "name": "IoT SiteWise",
            "group": "iot",
        },
    }


class IamPolicy(ResourceProvider):
    def __init__(self, options: PolicyOptions):
        """
        Iam policy

        :param options:
        """
        super().__init__()
        self.options = options

    @exception
    @ResourceAvailable(services="iam")
    def get_resources(self) -> List[Resource]:
        client = self.options.client("iam")
        if self.options.verbose:
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
    @ResourceAvailable(services="iam")
    def __init__(self, options: PolicyOptions):
        """
        Iam group

        :param options:
        """
        super().__init__()
        self.options = options
        self.client = options.client("iam")
        self.resources_found: List[Resource] = []

    @exception
    def get_resources(self) -> List[Resource]:

        if self.options.verbose:
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
    @ResourceAvailable(services="iam")
    def __init__(self, options: PolicyOptions):
        """
        Iam role

        :param options:
        """
        super().__init__()
        self.options = options
        self.client = options.client("iam")
        self.resources_found: List[Resource] = []

    @exception
    def get_resources(self) -> List[Resource]:

        if self.options.verbose:
            message_handler("Collecting data from IAM Roles...", "HEADER")
        paginator = self.client.get_paginator("list_roles")
        pages = paginator.paginate()

        resources_found = []
        for roles in pages:
            for data in roles["Roles"]:
                resource_digest = ResourceDigest(
                    id=data["RoleName"], type="aws_iam_role"
                )
                tag_response = self.client.list_role_tags(RoleName=data["RoleName"],)
                resources_found.append(
                    Resource(
                        digest=resource_digest,
                        name=data["RoleName"],
                        details="",
                        group="",
                        tags=resource_tags(tag_response),
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
                if assuming_service in Principals.principals:
                    principal = Principals.principals[assuming_service]
                    principal_found = Resource(
                        digest=ResourceDigest(
                            id=assuming_service, type=principal["type"],
                        ),
                        name=principal["name"],
                        details="principal",
                        group=principal["group"],
                    )
                else:
                    principal_found = Resource(
                        digest=ResourceDigest(id=assuming_service, type="aws_general"),
                        name=assuming_service,
                        details="principal",
                        group="general",
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
    def __init__(self, vpc_options: PolicyOptions):
        """
        Instance profile

        :param vpc_options:
        """
        super().__init__()
        self.vpc_options = vpc_options

    @exception
    def get_resources(self) -> List[Resource]:

        if self.vpc_options.verbose:
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
