from pathlib import Path
from typing import List, Dict

from diagrams import Diagram, Cluster, Edge

from shared.common import Resource, ResourceEdge, ResourceDigest, message_handler
from shared.error_handler import exception

PATH_DIAGRAM_OUTPUT = "./assets/diagrams/"
DIAGRAM_CLUSTER = "diagram_cluster"


class Mapsources:
    # diagrams modules that store classes that represent diagram elements
    diagrams_modules = [
        "analytics",
        "ar",
        "blockchain",
        "business",
        "compute",
        "cost",
        "database",
        "devtools",
        "enablement",
        "enduser",
        "engagement",
        "game",
        "general",
        "integration",
        "iot",
        "management",
        "media",
        "migration",
        "ml",
        "mobile",
        "network",
        "quantum",
        "robotics",
        "satellite",
        "security",
        "storage",
    ]

    # Class to mapping type resource from Terraform to Diagram Nodes
    mapresources = {
        "aws_lambda_function": "Lambda",
        "aws_emr_cluster": "EMRCluster",
        "aws_emr": "EMR",
        "aws_elasticsearch_domain": "ES",
        "aws_msk_cluster": "ManagedStreamingForKafka",
        "aws_sqs_queue_policy": "SQS",
        "aws_instance": "EC2",
        "aws_eks_cluster": "EKS",
        "aws_autoscaling_group": "AutoScaling",
        "aws_ecs_cluster": "ECS",
        "aws_db_instance": "RDS",
        "aws_elasticache_cluster": "ElastiCache",
        "aws_docdb_cluster": "DocumentDB",
        "aws_internet_gateway": "InternetGateway",
        "aws_nat_gateway": "NATGateway",
        "aws_elb_classic": "ELB",
        "aws_elb": "ELB",
        "aws_route_table": "RouteTable",
        "aws_subnet": "PublicSubnet",
        "aws_network_acl": "Nacl",
        "aws_vpc_peering_connection": "VPCPeering",
        "aws_vpc_endpoint_gateway": "Endpoint",
        "aws_iam_policy": "IAMPermissions",
        "aws_iam_user": "User",
        "aws_iam_group": "IAM",
        "aws_iam_role": "IAMRole",
        "aws_iam_instance_profile": "IAM",
        "aws_efs_file_system": "EFS",
        "aws_s3_bucket_policy": "S3",
        "aws_media_connect": "ElementalMediaconnect",
        "aws_media_convert": "ElementalMediaconvert",
        "aws_media_package": "ElementalMediapackage",
        "aws_media_store": "ElementalMediastore",
        "aws_media_tailor": "ElementalMediatailor",
        "aws_media_live": "ElementalMedialive",
        "aws_api_gateway_rest_api": "APIGateway",
        "aws_sagemaker": "Sagemaker",
        "aws_sagemaker_notebook_instance": "SagemakerNotebook",
        "aws_sagemaker_training_job": "SagemakerTrainingJob",
        "aws_sagemaker_model": "SagemakerModel",
        "aws_ssm_document": "SSM",
        "aws_cognito_identity_provider": "Cognito",
        "aws_iot_thing": "InternetOfThings",
        "aws_general": "General",
        "aws_appsync_graphql_api": "Appsync",
        "aws_iot_analytics": "IotAnalytics",
        "aws_securityhub_account": "SecurityHub",
        "aws_trusted_advisor": "TrustedAdvisor",
        "aws_kinesis_firehose": "KinesisDataFirehose",
        "aws_glue": "Glue",
        "aws_quicksight": "Quicksight",
        "aws_cloud9": "Cloud9",
        "aws_organizations_account": "Organizations",
        "aws_config": "Config",
        "aws_auto_scaling": "AutoScaling",
        "aws_backup": "Backup",
        "aws_cloudtrail": "Cloudtrail",
        "aws_cloudwatch": "Cloudwatch",
        "aws_data_pipeline": "DataPipeline",
        "aws_dms": "DMS",
        "aws_elastic_beanstalk_environment": "EB",
        "aws_fms": "FMS",
        "aws_global_accelerator": "GAX",
        "aws_inspector": "Inspector",
        "aws_cloudfront_distribution": "CloudFront",
        "aws_migration_hub": "MigrationHub",
        "aws_sns_topic": "SNS",
        "aws_vpc": "VPC",
        "aws_iot": "IotCore",
        "aws_iot_certificate": "IotCertificate",
        "aws_iot_policy": "IotPolicy",
        "aws_iot_type": "IotCore",  # TODO: need to fix with new diagram release
        "aws_iot_billing_group": "IotCore",  # TODO: need to fix with new diagram release
        "aws_iot_job": "IotJobs",
        "aws_alexa_skill": "IotAlexaSkill",
        "aws_acm": "ACM",
        "aws_mq": "MQ",
        "aws_athena": "Athena",
        "aws_artifact": "Artifact",
        "aws_batch": "Artifact",
        "aws_billingconsole": "General",  # TODO: need to fix with new diagram release
        "aws_ce": "CostExplorer",
        "aws_lex": "Lex",
        "aws_chime": "Chime",
        "aws_clouddirectory": "CloudDirectory",
        "aws_cloudformation": "Cloudformation",
        "aws_cloudhsm": "CloudHSM",
        "aws_cloudsearch": "Cloudsearch",
        "aws_codebuild": "Codebuild",
        "aws_codecommit": "Codecommit",
        "aws_codedeploy": "Codedeploy",
        "aws_codepipeline": "Codepipeline",
        "aws_codestar": "Codestar",
        "aws_discovery": "ApplicationDiscoveryService",
        "aws_dax": "DynamodbDax",
        "aws_deeplens": "Deeplens",
        "aws_delivery_logs": "General",  # TODO: need to fix with new diagram release
        "aws_diode": "General",  # TODO: need to fix with new diagram release
        "aws_directconnect": "DirectConnect",
        "aws_dlm": "General",  # TODO: need to fix with new diagram release
        "aws_ds": "DirectoryService",
        "aws_dynamodb": "Dynamodb",
        "aws_ecr": "EC2ContainerRegistry",
        "aws_efs": "ElasticFileSystemEFS",
        "aws_elastictranscoder": "ElasticTranscoder",
        "aws_events": "Eventbridge",
        "aws_freertos": "FreeRTOS",
        "aws_fsx": "Fsx",
        "aws_gamelift": "Gamelift",
        "aws_glacier": "S3Glacier",
        "aws_greengrass": "Greengrass",
        "aws_guardduty": "Guardduty",
        "aws_health": "General",  # TODO: need to fix with new diagram release
        "aws_iam": "IAM",
        "aws_importexport": "General",  # TODO: need to fix with new diagram release
        "aws_jellyfish": "General",  # TODO: need to fix with new diagram release
        "aws_kinesis": "Kinesis",
        "aws_kinesisanalytics": "KinesisDataAnalytics",
        "aws_kms": "KMS",
        "aws_lakeformation": "LakeFormation",
        "aws_license_manager": "LicenseManager",
        "aws_lightsail": "Lightsail",
        "aws_logs": "General",  # TODO: need to fix with new diagram release
        "aws_machinelearning": "MachineLearning",
        "aws_macie": "Macie",
        "aws_managedservices": "ManagedServices",
        "aws_marketplace": "Marketplace",
        "aws_mobile_hub": "General",  # TODO: need to fix with new diagram release
        "aws_monitoring": "General",  # TODO: need to fix with new diagram release
        "aws_opsworks": "Opsworks",
        "aws_pinpoint": "Pinpoint",
        "aws_polly": "Polly",
        "aws_qldb": "QLDB",
        "aws_ram": "ResourceAccessManager",
        "aws_redshift": "Redshift",
        "aws_rekognition": "Rekognition",
        "aws_resource_groups": "General",  # TODO: need to fix with new diagram release
        "aws_robomaker": "Robomaker",
        "aws_route53": "Route53",
        "aws_s3": "S3",
        "aws_secretsmanager": "SecretsManager",
        "aws_serverlessrepo": "ServerlessApplicationRepository",
        "aws_servicecatalog": "ServiceCatalog",
        "aws_servicediscovery": "General",  # TODO: need to fix with new diagram release
        "aws_ses": "SimpleEmailServiceSes",
        "aws_shield": "Shield",
        "aws_signer": "General",  # TODO: need to fix with new diagram release
        "aws_signin": "General",  # TODO: need to fix with new diagram release
        "aws_sms": "ServerMigrationService",
        "aws_sso": "SingleSignOn",
        "aws_states": "General",  # TODO: need to fix with new diagram release
        "aws_storagegateway": "StorageGateway",
        "aws_support": "Support",
        "aws_swf": "General",  # TODO: need to fix with new diagram release
        "aws_tagging": "General",  # TODO: need to fix with new diagram release
        "aws_transfer": "MigrationAndTransfer",
        "aws_translate": "Translate",
        "aws_tts": "General",  # TODO: need to fix with new diagram release
        "aws_vmie": "EC2",
        "aws_waf": "WAF",
        "aws_workdocs": "Workdocs",
        "aws_worklink": "Worklink",
        "aws_workmail": "Workmail",
        "aws_workspaces": "Workspaces",
        "aws_xray": "XRay",
        "aws_spotfleet": "EC2",
        "aws_sqs": "SQS",
        "aws_connect": "Connect",
        "aws_iotsitewise": "IotSitewise",
        "aws_neptune_cluster": "Neptune",
        "aws_alexa_for_business": "AlexaForBusiness",
        "aws_customer_gateway": "SiteToSiteVpn",
        "aws_vpn_connection": "SiteToSiteVpn",
        "aws_vpn_gateway": "SiteToSiteVpn",
        "aws_vpn_client_endpoint": "ClientVpn",
    }


def add_resource_to_group(ordered_resources, group, resource):
    if Mapsources.mapresources.get(resource.digest.type) is not None:
        if group in ordered_resources:
            ordered_resources[group].append(resource)
        else:
            ordered_resources[group] = [resource]


class BaseDiagram(object):
    def __init__(self, engine: str = "sfdp"):
        """
        Class to perform data aggregation, diagram generation and image saving

        The class accepts the following parameters
        :param engine:
        """
        self.engine = engine

    def build(
        self,
        resources: List[Resource],
        resource_relations: List[ResourceEdge],
        title: str,
        filename: str,
    ):
        self.make_directories()
        self.generate_diagram(resources, resource_relations, title, filename)

    @staticmethod
    def make_directories():
        Path(PATH_DIAGRAM_OUTPUT).mkdir(parents=True, exist_ok=True)

    def group_by_group(
        self, resources: List[Resource], initial_resource_relations: List[ResourceEdge]
    ) -> Dict[str, List[Resource]]:
        # Ordering Resource list to group resources into cluster
        ordered_resources: Dict[str, List[Resource]] = dict()
        for resource in resources:
            if Mapsources.mapresources.get(resource.digest.type) is not None:
                if resource.group in ordered_resources:
                    ordered_resources[resource.group].append(resource)
                else:
                    ordered_resources[resource.group] = [resource]
        return ordered_resources

    def process_relationships(
        self,
        grouped_resources: Dict[str, List[Resource]],
        resource_relations: List[ResourceEdge],
    ) -> List[ResourceEdge]:
        return resource_relations

    @exception
    def generate_diagram(
        self,
        resources: List[Resource],
        initial_resource_relations: List[ResourceEdge],
        title: str,
        filename: str,
    ):
        ordered_resources = self.group_by_group(resources, initial_resource_relations)
        relations = self.process_relationships(
            ordered_resources, initial_resource_relations
        )

        output_filename = PATH_DIAGRAM_OUTPUT + filename
        with Diagram(
            name=title,
            filename=output_filename,
            direction="TB",
            show=False,
            graph_attr={"nodesep": "2.0", "ranksep": "1.0", "splines": "curved"},
        ) as d:
            d.dot.engine = self.engine

            self.draw_diagram(ordered_resources=ordered_resources, relations=relations)

        message_handler("\n\nPNG diagram generated", "HEADER")
        message_handler("Check your diagram: " + output_filename + ".png", "OKBLUE")

    def draw_diagram(self, ordered_resources, relations):
        already_drawn_elements = {}

        # Import all AWS nodes
        for module in Mapsources.diagrams_modules:
            exec("from diagrams.aws." + module + " import *")

        nodes: Dict[ResourceDigest, any] = {}
        # Iterate resources to draw it
        for group_name in ordered_resources:
            if group_name == "":
                for resource in ordered_resources[group_name]:
                    node = eval(Mapsources.mapresources.get(resource.digest.type))(
                        resource.name
                    )
                    nodes[resource.digest] = node
            else:
                with Cluster(group_name.capitalize() + " resources") as cluster:
                    nodes[ResourceDigest(id=group_name, type=DIAGRAM_CLUSTER)] = cluster
                    for resource in ordered_resources[group_name]:
                        node = eval(Mapsources.mapresources.get(resource.digest.type))(
                            resource.name
                        )
                        nodes[resource.digest] = node

        for resource_relation in relations:
            if resource_relation.from_node == resource_relation.to_node:
                continue
            if (
                resource_relation.from_node in nodes
                and resource_relation.to_node in nodes
            ):
                from_node = nodes[resource_relation.from_node]
                to_node = nodes[resource_relation.to_node]
                if resource_relation.from_node not in already_drawn_elements:
                    already_drawn_elements[resource_relation.from_node] = {}
                if (
                    resource_relation.to_node
                    not in already_drawn_elements[resource_relation.from_node]
                ):
                    from_node >> Edge(label=resource_relation.label) >> to_node
                    already_drawn_elements[resource_relation.from_node][
                        resource_relation.to_node
                    ] = True


class NoDiagram(BaseDiagram):
    def __init__(self):
        """
        Special class that doesn't generate any image.

        Command should be refactored not to have such class
        """
        super().__init__("")

    def generate_diagram(
        self,
        resources: List[Resource],
        resource_relations: List[ResourceEdge],
        title: str,
        filename: str,
    ):
        pass

    def build(
        self,
        resources: List[Resource],
        resource_relations: List[ResourceEdge],
        title: str,
        filename: str,
    ):
        pass
