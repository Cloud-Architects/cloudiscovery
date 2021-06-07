MX_FILE = """<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" modified="2020-09-01T05:47:00.000Z" agent="cloudiscovery" etag="123456" 
    version="13.7.7" type="device">
   <diagram id="123456654321" name="Page-1"><MX_GRAPH></diagram>
</mxfile>
"""

DIAGRAM_HEADER = """<?xml version="1.0" encoding="UTF-8"?>
<mxGraphModel dx="1186" dy="773" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" 
    pageScale="1" pageWidth="827" pageHeight="1169" math="0" shadow="0">
   <root>
      <mxCell id="0" />
      <mxCell id="1" parent="0" />"""

DIAGRAM_SUFFIX = """
   </root>
</mxGraphModel>"""

CELL_TEMPLATE = """
<mxCell id="{CELL_IDX}" value="{TITLE}" style="{STYLE}" vertex="1" parent="1">
   <mxGeometry x="{X}" y="{Y}" width="50" height="50" as="geometry" />
</mxCell>
"""


# from https://github.com/jgraph/drawio/blob/master/src/main/webapp/js/diagramly/sidebar/Sidebar-AWS4.js
gn = "mxgraph.aws4"

s = 1
w = s * 100
h = s * 100
w2 = s * 78


def _add_general_resources(styles, provider):
    if provider == "aws":
        n3 = (
        "gradientDirection=north;outlineConnect=0;fontColor=#232F3E;gradientColor=#505863;fillColor=#1E262E;"
        "strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;"
        "fontSize=12;fontStyle=0;aspect=fixed;shape=mxgraph.aws4."
        )
    elif provider == "ibm":
        n3 = (
        "gradientDirection=north;outlineConnect=0;fontColor=#232F3E;gradientColor=#505863;fillColor=#1E262E;"
        "strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;"
        "fontSize=12;fontStyle=0;aspect=fixed;shape=mxgraph.ibm."
        )
        styles["ibm_general"] = n3 + "resourceIcon;resIcon=" + "mxgraph.ibm" + ".general;"

def _add_analytics_resources(styles, provider):
    if provider == "aws":
        n2 = (
        "outlineConnect=0;fontColor=#232F3E;gradientColor=#945DF2;gradientDirection=north;fillColor=#5A30B5;"
        "strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;"
        "fontSize=12;fontStyle=0;aspect=fixed;shape=mxgraph.aws4."
        )
        styles["aws_athena"] = n2 + "resourceIcon;resIcon=" + gn + ".athena;"
        styles["aws_elasticsearch_domain"] = (
            n2 + "resourceIcon;resIcon=" + gn + ".elasticsearch_service;"
        )
        styles["aws_emr"] = n2 + "resourceIcon;resIcon=" + gn + ".emr;"
        styles["aws_emr_cluster"] = n2 + "resourceIcon;resIcon=" + gn + ".emr;"
        styles["aws_kinesis"] = n2 + "resourceIcon;resIcon=" + gn + ".kinesis;"
        styles["aws_kinesisanalytics"] = (
            n2 + "resourceIcon;resIcon=" + gn + ".kinesis_data_analytics;"
        )
        styles["aws_kinesis_firehose"] = (
            n2 + "resourceIcon;resIcon=" + gn + ".kinesis_data_firehose;"
        )
        styles["aws_quicksight"] = n2 + "resourceIcon;resIcon=" + gn + ".quicksight;"
        styles["aws_redshift"] = n2 + "resourceIcon;resIcon=" + gn + ".redshift;"
        styles["aws_data_pipeline"] = n2 + "resourceIcon;resIcon=" + gn + ".data_pipeline;"
        styles["aws_msk_cluster"] = (
            n2 + "resourceIcon;resIcon=" + gn + ".managed_streaming_for_kafka;"
        )
        styles["aws_glue"] = n2 + "resourceIcon;resIcon=" + gn + ".glue;"
        styles["aws_lakeformation"] = n2 + "resourceIcon;resIcon=" + gn + ".lake_formation;"
    else:
        n2 = (
        "outlineConnect=0;fontColor=#232F3E;gradientColor=#945DF2;gradientDirection=north;fillColor=#5A30B5;"
        "strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;"
        "fontSize=12;fontStyle=0;aspect=fixed;shape=mxgraph.ibm."
        )
        styles["aws_athena"] = n2 + "resourceIcon;resIcon=" + "mxgraph.ibm" + ".athena;"
        styles["aws_elasticsearch_domain"] = (
            n2 + "resourceIcon;resIcon=" + "mxgraph.ibm" + ".elasticsearch_service;"
        )
        styles["aws_emr"] = n2 + "resourceIcon;resIcon=" + "mxgraph.ibm" + ".emr;"
        styles["aws_emr_cluster"] = n2 + "resourceIcon;resIcon=" + "mxgraph.ibm" + ".emr;"
        styles["aws_kinesis"] = n2 + "resourceIcon;resIcon=" + "mxgraph.ibm" + ".kinesis;"
        styles["aws_kinesisanalytics"] = (
            n2 + "resourceIcon;resIcon=" + "mxgraph.ibm" + ".kinesis_data_analytics;"
        )
        styles["aws_kinesis_firehose"] = (
            n2 + "resourceIcon;resIcon=" + "mxgraph.ibm" + ".kinesis_data_firehose;"
        )
        styles["aws_quicksight"] = n2 + "resourceIcon;resIcon=" + "mxgraph.ibm" + ".quicksight;"
        styles["aws_redshift"] = n2 + "resourceIcon;resIcon=" + "mxgraph.ibm" + ".redshift;"
        styles["aws_data_pipeline"] = n2 + "resourceIcon;resIcon=" + "mxgraph.ibm" + ".data_pipeline;"
        styles["aws_msk_cluster"] = (
            n2 + "resourceIcon;resIcon=" + "mxgraph.ibm" + ".managed_streaming_for_kafka;"
        )
        styles["aws_glue"] = n2 + "resourceIcon;resIcon=" + "mxgraph.ibm" + ".glue;"
        styles["aws_lakeformation"] = n2 + "resourceIcon;resIcon=" + "mxgraph.ibm" + ".lake_formation;"

def _add_application_integration_resources(styles, provider):
    if provider == "aws":
        n2 = (
        "outlineConnect=0;fontColor=#232F3E;gradientColor=#F34482;gradientDirection=north;fillColor=#BC1356;"
        "strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;"
        "fontSize=12;fontStyle=0;aspect=fixed;shape=mxgraph.aws4."
        )
        styles["aws_sns_topic"] = n2 + "resourceIcon;resIcon=" + gn + ".sns;"
        styles["aws_sqs"] = n2 + "resourceIcon;resIcon=" + gn + ".sqs;"
        styles["aws_appsync_graphql_api"] = n2 + "resourceIcon;resIcon=" + gn + ".appsync;"
        styles["aws_events"] = n2 + "resourceIcon;resIcon=" + gn + ".eventbridge;"

def _add_compute_resources(styles, provider):
    if provider == "aws":
        n = (
        "outlineConnect=0;fontColor=#232F3E;gradientColor=none;fillColor=#D05C17;strokeColor=none;dashed=0;"
        "verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;"
        "pointerEvents=1;shape=mxgraph.aws4."
        )
        n2 = (
        "outlineConnect=0;fontColor=#232F3E;gradientColor=#F78E04;gradientDirection=north;fillColor=#D05C17;"
        "strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;"
        "fontSize=12;fontStyle=0;aspect=fixed;shape=mxgraph.aws4."
        )

        styles["aws_instance"] = n2 + "resourceIcon;resIcon=" + gn + ".ec2;"
        styles["aws_autoscaling_group"] = (
        n2 + "resourceIcon;resIcon=" + gn + ".auto_scaling2;"
        )
        styles["aws_batch"] = n2 + "resourceIcon;resIcon=" + gn + ".batch;"
        styles["aws_elastic_beanstalk_environment"] = (
        n2 + "resourceIcon;resIcon=" + gn + ".elastic_beanstalk;"
        )
        styles["aws_lambda_function"] = n + "lambda_function;"

def _add_container_resources(styles, provider):
    if provider == "aws":
        n2 = (
        "outlineConnect=0;fontColor=#232F3E;gradientColor=#F78E04;gradientDirection=north;fillColor=#D05C17;"
        "strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;"
        "fontSize=12;fontStyle=0;aspect=fixed;shape=mxgraph.aws4."
        )
        styles["aws_eks_cluster"] = n2 + "resourceIcon;resIcon=" + gn + ".eks;"
        styles["aws_ecr"] = n2 + "resourceIcon;resIcon=" + gn + ".ecr;"
        styles["aws_ecs_cluster"] = n2 + "resourceIcon;resIcon=" + gn + ".ecs;"


def _add_customer_engagement_resources(styles, provider):
    if provider == "aws":
        n2 = (
        "outlineConnect=0;fontColor=#232F3E;gradientColor=#4D72F3;gradientDirection=north;fillColor=#3334B9;"
        "strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;"
        "fontSize=12;fontStyle=0;aspect=fixed;shape=mxgraph.aws4."
        )
        styles["aws_connect"] = n2 + "resourceIcon;resIcon=" + gn + ".connect;"
        styles["aws_pinpoint"] = n2 + "resourceIcon;resIcon=" + gn + ".pinpoint;"
        styles["aws_ses"] = n2 + "resourceIcon;resIcon=" + gn + ".simple_email_service;"


def _add_database_resources(styles, provider):
    if provider == "aws":
        n = (
        "outlineConnect=0;fontColor=#232F3E;gradientColor=none;fillColor=#3334B9;strokeColor=none;dashed=0;"
        "verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;"
        "pointerEvents=1;shape=mxgraph.aws4."
        )
        n2 = (
        "outlineConnect=0;fontColor=#232F3E;gradientColor=#4D72F3;gradientDirection=north;fillColor=#3334B9;"
        "strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;"
        "fontSize=12;fontStyle=0;aspect=fixed;shape=mxgraph.aws4."
        )
        styles["aws_docdb_cluster"] = (
        n2 + "resourceIcon;resIcon=" + gn + ".documentdb_with_mongodb_compatibility;"
        )
        styles["aws_dynamodb"] = n2 + "resourceIcon;resIcon=" + gn + ".dynamodb;"
        styles["aws_elasticache_cluster"] = (
        n2 + "resourceIcon;resIcon=" + gn + ".elasticache;"
        )
        styles["aws_neptune_cluster"] = n2 + "resourceIcon;resIcon=" + gn + ".neptune;"
        styles["aws_redshift"] = n2 + "resourceIcon;resIcon=" + gn + ".redshift;"

        styles["aws_db_instance"] = n + "rds_instance;"
        styles["aws_dax"] = n + "dynamodb_dax;"


def _add_ml_resources(styles, provider):
    if provider == "aws":
        n2 = (
        "outlineConnect=0;fontColor=#232F3E;gradientColor=#4AB29A;gradientDirection=north;fillColor=#116D5B;"
        "strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;"
        "fontSize=12;fontStyle=0;aspect=fixed;shape=mxgraph.aws4."
        )
        styles["aws_sagemaker"] = n2 + "resourceIcon;resIcon=" + gn + ".sagemaker;"

def _add_management_governance_resources(styles, provider):
    if provider == "aws":
        n2 = (
        "outlineConnect=0;fontColor=#232F3E;gradientColor=#F34482;gradientDirection=north;fillColor=#BC1356;"
        "strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;"
        "fontSize=12;fontStyle=0;aspect=fixed;shape=mxgraph.aws4."
        )
        styles["aws_cloudwatch"] = n2 + "resourceIcon;resIcon=" + gn + ".cloudwatch_2;"
        styles["aws_autoscaling_group"] = (
        n2 + "resourceIcon;resIcon=" + gn + ".autoscaling;"
        )
        styles["aws_auto_scaling"] = n2 + "resourceIcon;resIcon=" + gn + ".autoscaling;"
        styles["aws_cloudformation"] = (
        n2 + "resourceIcon;resIcon=" + gn + ".cloudformation;"
        )

def _add_network_resources(styles, provider):
    if provider == "aws":
        n = (
            "outlineConnect=0;fontColor=#232F3E;gradientColor=none;fillColor=#5A30B5;strokeColor=none;dashed=0;"
            "verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;"
            "pointerEvents=1;shape=mxgraph.aws4."
        )
        n2 = (
            "outlineConnect=0;fontColor=#232F3E;gradientColor=#945DF2;gradientDirection=north;fillColor=#5A30B5;"
            "strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;"
            "fontSize=12;fontStyle=0;aspect=fixed;shape=mxgraph.aws4."
        )
        styles["aws_api_gateway_rest_api"] = (
            n2 + "resourceIcon;resIcon=" + gn + ".api_gateway;"
        )
        styles["aws_cloudfront_distribution"] = (
            n2 + "resourceIcon;resIcon=" + gn + ".cloudfront;"
        )
        styles["aws_vpc"] = n2 + "resourceIcon;resIcon=" + gn + ".vpc;"
        styles["aws_vpn_client_endpoint"] = (
            n2 + "resourceIcon;resIcon=" + gn + ".client_vpn;"
        )
        styles["aws_elb"] = n2 + "resourceIcon;resIcon=" + gn + ".elastic_load_balancing;"
        styles["aws_directconnect"] = n2 + "resourceIcon;resIcon=" + gn + ".direct_connect;"
        styles["aws_global_accelerator"] = (
            n2 + "resourceIcon;resIcon=" + gn + ".global_accelerator;"
        )
        styles["aws_route_table"] = n + "route_table;"
        styles["aws_vpc_endpoint_gateway"] = n + "gateway;"
        styles["aws_internet_gateway"] = n + "internet_gateway;"
        styles["aws_nat_gateway"] = n + "nat_gateway;"
        styles["aws_network_acl"] = n + "network_access_control_list;"
        styles["aws_elb_classic"] = n + "classic_load_balancer;"
        styles["aws_vpn_connection"] = n + "vpn_connection;"
        styles["aws_vpn_gateway"] = n + "vpn_gateway;"
    else:
        styles["ibm_route_table"] = (
            "outlineConnect=0;fontColor=#232F3E;gradientColor=none;fillColor=#5A30B5;strokeColor=none;dashed=0;"
            "verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;"
            "pointerEvents=1;shape=mxgraph.aws4.route_table;"
        )
        styles["ibm_security_group"] = 'fontStyle=0;verticalAlign=top;align=center;spacingTop=-2;fillColor=none;'
        styles["ibm_security_group"] = styles["ibm_security_group"] + 'rounded=0;whiteSpace=wrap;html=1;'
        styles["ibm_security_group"] = styles["ibm_security_group"] + 'strokeColor=#FF0000;strokeWidth=2;'
        styles["ibm_security_group"] = styles["ibm_security_group"] + 'dashed=1;container=1;collapsible=0;'
        styles["ibm_security_group"] = styles["ibm_security_group"] + 'expand=0;recursiveResize=0;'
        styles["ibm_network_acl"] = 'shape=mxgraph.ibm.box;prType=subnet;fontStyle=0;verticalAlign=top;'
        styles["ibm_network_acl"] = styles["ibm_network_acl"] + 'align=left;spacingLeft=32;spacingTop=4;'
        styles["ibm_network_acl"] = styles["ibm_network_acl"] + 'fillColor=#E6F0E2;rounded=0;whiteSpace=wrap;'
        styles["ibm_network_acl"] = styles["ibm_network_acl"] + 'html=1;strokeColor=#00882B;strokeWidth=1;dashed=0;'
        styles["ibm_network_acl"] = styles["ibm_network_acl"] + 'container=1;spacing=-4;collapsible=0;expand=0;'
        styles["ibm_network_acl"] = styles["ibm_network_acl"] + 'recursiveResize=0;'


def _add_storage_resources(styles, provider):
    if provider == "aws":
        n = (
        "outlineConnect=0;fontColor=#232F3E;gradientColor=none;fillColor=#277116;strokeColor=none;dashed=0;"
        "verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;"
        "pointerEvents=1;shape=mxgraph.aws4."
        )
        n2 = (
        "outlineConnect=0;fontColor=#232F3E;gradientColor=#60A337;gradientDirection=north;fillColor=#277116;"
        "strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;"
        "fontSize=12;fontStyle=0;aspect=fixed;shape=mxgraph.aws4."
        )

        styles["aws_efs_file_system"] = (
        n2 + "resourceIcon;resIcon=" + gn + ".elastic_file_system;"
        )
        styles["aws_fsx"] = n2 + "resourceIcon;resIcon=" + gn + ".fsx;"

        styles["aws_s3"] = n + "bucket;"


def build_styles(provider):
    styles = {}
    _add_general_resources(styles, provider)
    _add_analytics_resources(styles, provider)
    _add_application_integration_resources(styles, provider)
    _add_compute_resources(styles, provider)
    _add_container_resources(styles, provider)
    _add_customer_engagement_resources(styles, provider)
    _add_database_resources(styles, provider)
    _add_ml_resources(styles, provider)
    _add_management_governance_resources(styles, provider)
    _add_network_resources(styles, provider)
    _add_storage_resources(styles, provider)
    return styles
