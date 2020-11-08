import base64
import zlib
from pathlib import Path
from typing import List, Dict

from diagrams import Diagram, Cluster, Edge

from shared.common import Resource, ResourceEdge, ResourceDigest, message_handler
from shared.diagramsnet import DIAGRAM_HEADER, DIAGRAM_SUFFIX, MX_FILE, CELL_TEMPLATE
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

    styles = {
        "aws_vpn_gateway": "outlineConnect=0;fontColor=#232F3E;gradientColor=none;fillColor=#5A30B5;strokeColor=none;"
        "dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;"
        "fontStyle=0;aspect=fixed;pointerEvents=1;shape=mxgraph.aws4.vpn_gateway;",
        "aws_general": "gradientDirection=north;outlineConnect=0;fontColor=#232F3E;gradientColor=#505863;"
        "fillColor=#1E262E;strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;"
        "align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;"
        "resIcon=mxgraph.aws4.general;",
        "aws_lambda_function": "outlineConnect=0;fontColor=#232F3E;gradientColor=none;fillColor=#D05C17;"
        "strokeColor=none;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;"
        "html=1;fontSize=12;fontStyle=0;aspect=fixed;pointerEvents=1;"
        "shape=mxgraph.aws4.lambda_function;",
        "aws_route_table": "outlineConnect=0;fontColor=#232F3E;gradientColor=none;fillColor=#5A30B5;strokeColor=none;"
        "dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;"
        "fontStyle=0;aspect=fixed;pointerEvents=1;shape=mxgraph.aws4.route_table;",
        "aws_internet_gateway": "outlineConnect=0;fontColor=#232F3E;gradientColor=none;fillColor=#5A30B5;"
        "strokeColor=none;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;"
        "align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;pointerEvents=1;"
        "shape=mxgraph.aws4.internet_gateway;",
        "aws_elb": "outlineConnect=0;fontColor=#232F3E;gradientColor=none;fillColor=#5A30B5;strokeColor=none;"
        "dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;"
        "fontStyle=0;aspect=fixed;pointerEvents=1;shape=mxgraph.aws4.application_load_balancer;",
        "aws_network_acl": "outlineConnect=0;fontColor=#232F3E;gradientColor=none;fillColor=#5A30B5;strokeColor=none;"
        "dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;"
        "fontStyle=0;aspect=fixed;pointerEvents=1;shape=mxgraph.aws4.network_access_control_list;",
        "aws_vpc_endpoint_gateway": "outlineConnect=0;fontColor=#232F3E;gradientColor=none;fillColor=#5A30B5;"
        "strokeColor=none;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;"
        "align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;pointerEvents=1;"
        "shape=mxgraph.aws4.endpoint;",
        "aws_ecs_cluster": "outlineConnect=0;fontColor=#232F3E;gradientColor=#F78E04;gradientDirection=north;"
        "fillColor=#D05C17;strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;"
        "verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;"
        "shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.ecs;",
        "aws_instance": "outlineConnect=0;fontColor=#232F3E;gradientColor=#F78E04;gradientDirection=north;"
        "fillColor=#D05C17;strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;"
        "verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;"
        "shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.ec2;",
        "aws_s3": "outlineConnect=0;fontColor=#232F3E;gradientColor=none;fillColor=#277116;strokeColor=none;"
        "dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;"
        "fontStyle=0;aspect=fixed;pointerEvents=1;shape=mxgraph.aws4.bucket;",
        "aws_db_instance": "outlineConnect=0;fontColor=#232F3E;gradientColor=none;fillColor=#3334B9;strokeColor=none;"
        "dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;"
        "fontStyle=0;aspect=fixed;pointerEvents=1;shape=mxgraph.aws4.rds_instance;",
        "aws_dynamodb": "outlineConnect=0;fontColor=#232F3E;gradientColor=none;fillColor=#3334B9;strokeColor=none;"
        "dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;"
        "fontStyle=0;aspect=fixed;pointerEvents=1;shape=mxgraph.aws4.table;",
        "aws_sqs": "outlineConnect=0;fontColor=#232F3E;gradientColor=none;fillColor=#BC1356;strokeColor=none;dashed=0;"
        "verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;"
        "aspect=fixed;pointerEvents=1;shape=mxgraph.aws4.queue;",
        "aws_sns_topic": "outlineConnect=0;fontColor=#232F3E;gradientColor=none;fillColor=#BC1356;strokeColor=none;"
        "dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;"
        "fontStyle=0;aspect=fixed;pointerEvents=1;shape=mxgraph.aws4.topic;",
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


class VPCDiagramsNetDiagram(BaseDiagram):
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
        diagram = self.build_diagram(ordered_resources, relations)
        output_filename = PATH_DIAGRAM_OUTPUT + filename + ".drawio"

        with open(output_filename, "w") as diagram_file:
            diagram_file.write(diagram)

    @staticmethod
    def decode_inflate(value: str):
        decoded = base64.b64decode(value)
        try:
            result = zlib.decompress(decoded, -15)
        # pylint: disable=broad-except
        except Exception:
            result = decoded
        return result.decode("utf-8")

    @staticmethod
    def deflate_encode(value: str):
        return base64.b64encode(zlib.compress(value.encode("utf-8"))[2:-4]).decode(
            "utf-8"
        )

    # pylint: disable=too-many-locals
    def build_diagram(
        self,
        resources: Dict[str, List[Resource]],
        resource_relations: List[ResourceEdge],
    ):
        mx_graph_model = DIAGRAM_HEADER
        cell_id = 1

        vpc_resource = None
        for _, resource_group in resources.items():
            for resource in resource_group:
                if resource.digest.type == "aws_vpc":
                    if vpc_resource is None:
                        vpc_resource = resource
                    else:
                        raise Exception("Only one VPC in a region is supported now")
        if vpc_resource is None:
            raise Exception("Only one VPC in a region is supported now")

        added_resources: List[ResourceDigest] = []

        vpc_cell = (
            '<mxCell id="zB3y0Dp3mfEUP9Fxs3Er-{0}" value="{1}" style="points=[[0,0],[0.25,0],[0.5,0],'
            "[0.75,0],[1,0],[1,0.25],[1,0.5],[1,0.75],[1,1],[0.75,1],[0.5,1],[0.25,1],[0,1],[0,0.75],"
            "[0,0.5],[0,0.25]];outlineConnect=0;gradientColor=none;html=1;whiteSpace=wrap;fontSize=12;"
            "fontStyle=0;shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_vpc;strokeColor=#248814;"
            'fillColor=none;verticalAlign=top;align=left;spacingLeft=30;fontColor=#AAB7B8;dashed=0;" '
            'parent="1" vertex="1"><mxGeometry x="0" y="0" width="1040" height="1000" as="geometry" />'
            "</mxCell>".format(cell_id, vpc_resource.name)
        )
        cell_id += 1
        mx_graph_model += vpc_cell

        public_subnet_x = 80
        public_subnet_y = 80
        cell_id += 1
        # pylint: disable=line-too-long
        public_subnet = (
            '<mxCell id="public_area_id" value="Public subnet" style="points=[[0,0],[0.25,0],[0.5,0],'
            "[0.75,0],[1,0],[1,0.25],[1,0.5],[1,0.75],[1,1],[0.75,1],[0.5,1],[0.25,1],[0,1],[0,0.75],"
            "[0,0.5],[0,0.25]];outlineConnect=0;gradientColor=none;html=1;whiteSpace=wrap;fontSize=12;"
            "fontStyle=0;shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_security_group;grStroke=0;"
            "strokeColor=#248814;fillColor=#E9F3E6;verticalAlign=top;align=left;spacingLeft=30;"
            'fontColor=#248814;dashed=0;" vertex="1" parent="1"><mxGeometry x="{X}" y="{Y}" width="420" '
            'height="500" as="geometry" /></mxCell>'.format_map(
                {"X": str(public_subnet_x), "Y": str(public_subnet_y)}
            )
        )
        mx_graph_model += public_subnet

        mx_graph_model = self.render_subnet_items(
            added_resources,
            mx_graph_model,
            "{public subnet}",
            public_subnet_x,
            public_subnet_y,
            resource_relations,
            resources,
        )

        private_subnet_x = 580
        private_subnet_y = 80
        cell_id += 1
        private_subnet = (
            '<mxCell id="private_area_id" value="Private subnet" style="points=[[0,0],[0.25,0],'
            "[0.5,0],[0.75,0],[1,0],[1,0.25],[1,0.5],[1,0.75],[1,1],[0.75,1],[0.5,1],[0.25,1],[0,1],"
            "[0,0.75],[0,0.5],[0,0.25]];outlineConnect=0;gradientColor=none;html=1;whiteSpace=wrap;"
            "fontSize=12;fontStyle=0;shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_security_group;"
            "grStroke=0;strokeColor=#147EBA;fillColor=#E6F2F8;verticalAlign=top;align=left;"
            'spacingLeft=30;fontColor=#147EBA;dashed=0;" vertex="1" parent="1"><mxGeometry '
            'x="{X}" y="{Y}" width="420" height="500" as="geometry" /></mxCell>'.format_map(
                {"X": str(private_subnet_x), "Y": str(private_subnet_y)}
            )
        )
        mx_graph_model += private_subnet

        mx_graph_model = self.render_subnet_items(
            added_resources,
            mx_graph_model,
            "{private subnet}",
            private_subnet_x,
            private_subnet_y,
            resource_relations,
            resources,
        )

        count = 0
        row = 0
        for _, resource_group in resources.items():
            for resource in resource_group:
                if resource.digest.type in ["aws_subnet", "aws_vpc"]:
                    continue
                if resource.digest not in added_resources:
                    added_resources.append(resource.digest)
                    style = (
                        Mapsources.styles[resource.digest.type]
                        if resource.digest.type in Mapsources.styles
                        else Mapsources.styles["aws_general"]
                    )
                    cell = CELL_TEMPLATE.format_map(
                        {
                            "CELL_IDX": resource.digest.to_string(),
                            "X": str(count * 140 + public_subnet_x + 40),
                            "Y": str(580 + row * 100 + 40),
                            "STYLE": style.replace("fontSize=12", "fontSize=8"),
                            "TITLE": resource.name,
                        }
                    )
                    count += 1
                    mx_graph_model += cell
                    if count % 6 == 0:
                        row += 1
                        count = 0

        mx_graph_model += DIAGRAM_SUFFIX
        return MX_FILE.replace("<MX_GRAPH>", self.deflate_encode(mx_graph_model))

    # pylint: disable=too-many-locals,too-many-arguments
    def render_subnet_items(
        self,
        added_resources,
        mx_graph_model,
        subnet_id,
        subnet_x,
        subnet_y,
        resource_relations,
        resources,
    ):
        count = 0
        row = 0
        # pylint: disable=too-many-nested-blocks
        for relation in resource_relations:
            if relation.to_node == ResourceDigest(id=subnet_id, type="aws_subnet"):
                for _, resource_group in resources.items():
                    for resource in resource_group:
                        if (
                            resource.digest == relation.from_node
                            and relation.from_node not in added_resources
                        ):
                            added_resources.append(relation.from_node)
                            style = (
                                Mapsources.styles[relation.from_node.type]
                                if relation.from_node.type in Mapsources.styles
                                else Mapsources.styles["aws_general"]
                            )

                            cell = CELL_TEMPLATE.format_map(
                                {
                                    "CELL_IDX": relation.from_node.to_string(),
                                    "X": str(count * 140 + subnet_x + 40),
                                    "Y": str(subnet_y + row * 100 + 40),
                                    "STYLE": style.replace("fontSize=12", "fontSize=8"),
                                    "TITLE": resource.name,
                                }
                            )
                            count += 1
                            mx_graph_model += cell
                            if count % 3 == 0:
                                row += 1
                                count = 0
        return mx_graph_model
