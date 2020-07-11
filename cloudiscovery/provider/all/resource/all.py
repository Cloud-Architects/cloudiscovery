import collections
import functools
import re
from concurrent.futures.thread import ThreadPoolExecutor
from typing import List, Optional

from botocore.exceptions import UnknownServiceError
from botocore.loaders import Loader

from provider.all.command import AllOptions
from shared.common import (
    ResourceProvider,
    Resource,
    ResourceDigest,
    message_handler,
    ResourceAvailable,
    log_critical,
)
from shared.common_aws import get_paginator, resource_tags

OMITTED_RESOURCES = [
    "aws_cloudhsm_available_zone",
    "aws_cloudhsm_hapg",
    "aws_cloudhsm_hsm",
    "aws_cloudhsm_luna_client",
    "aws_dax_default_parameter",
    "aws_dax_parameter_group",
    "aws_ec2_reserved_instances_offering",
    "aws_ec2_snapshot",
    "aws_ec2_spot_price_history",
    "aws_ssm_available_patch",
    "aws_ssm_document",
    "aws_polly_voice",
    "aws_lightsail_blueprint",
    "aws_lightsail_bundle",
    "aws_lightsail_region",
    "aws_elastictranscoder_preset",
    "aws_ec2_vpc_endpoint_service",
    "aws_dms_endpoint_type",
    "aws_elasticache_service_update",
    "aws_elasticache_cache_parameter_group",
    "aws_rds_source_region",
    "aws_ssm_association",
    "aws_ssm_patch_baseline",
    "aws_ec2_prefix",
    "aws_ec2_image",
    "aws_ec2_region",
    "aws_opsworks_operating_system",
    "aws_rds_account_attribute",
    "aws_route53_geo_location",
    "aws_redshift_cluster_track",
    "aws_directconnect_location",
    "aws_dms_account_attribute",
    "aws_securityhub_standard",
    "aws_ram_resource_type",
    "aws_ram_permission",
    "aws_ec2_account_attribute",
    "aws_elasticbeanstalk_available_solution_stack",
    "aws_redshift_account_attribute",
    "aws_opsworks_user_profile",
    "aws_directconnect_direct_connect_gateway_association",  # DirectConnect resources endpoint are complicated
    "aws_directconnect_direct_connect_gateway_attachment",
    "aws_directconnect_interconnect",
    "aws_dms_replication_task_assessment_result",
    "aws_ec2_fpga_image",
    "aws_ec2_launch_template_version",
    "aws_ec2_reserved_instancesing",
    "aws_ec2_spot_datafeed_subscription",
    "aws_ec2_transit_gateway_multicast_domain",
    "aws_elasticbeanstalk_configuration_option",
    "aws_elasticbeanstalk_platform_version",
    "aws_iam_credential_report",
    "aws_iam_account_password_policy",
    "aws_importexport_job",
    "aws_iot_o_taupdate",
    "aws_iot_default_authorizer",
    "aws_workspaces_account",
    "aws_workspaces_account_modification",
    "aws_rds_export_task",
    "aws_rds_custom_availability_zone",
    "aws_rds_installation_media",
    "aws_rds_d_bsecurity_group",
    "aws_translate_text_translation_job",
    "aws_rekognition_project",
    "aws_rekognition_stream_processor",
    "aws_sdb_domain",
    "aws_redshift_table_restore_status",
    "aws_iot_v2_logging_level",
    "aws_license_manager_resource_inventory",
    "aws_license_manager_license_configuration",
    "aws_logs_query_definition",
    "aws_autoscaling_scaling_activity",
    "aws_cloudwatch_metric",
    "aws_organizations_handshakes_for_organization",
    "aws_config_organization_config_rule",
    "aws_organizations_root",
    "aws_organizations_delegated_administrator",
    "aws_organizations_create_account_status",
    "aws_config_organization_conformance_pack_status",
    "aws_config_organization_conformance_pack",
    "aws_ec2_reserved_instances_listing",
    "aws_redshift_cluster_security_group",
    "aws_guardduty_organization_admin_account",
    "aws_elasticache_cache_security_group",
    "aws_organizations_aws_service_access_for_organization",
    "aws_organizations_account",
    "aws_config_organization_config_rule_status",
    "aws_dynamodb_backup",
    "aws_ec2_prefix_list",
    "aws_route53_hosted_zones_by_name",
]

# Trying to fix documentation errors or its lack made by "happy pirates" at AWS
REQUIRED_PARAMS_OVERRIDE = {
    "batch": {"ListJobs": ["jobQueue"]},
    "cloudformation": {
        "DescribeStackEvents": ["stackName"],
        "DescribeStackResources": ["stackName"],
        "GetTemplate": ["stackName"],
        "ListTypeVersions": ["arn"],
    },
    "codecommit": {"GetBranch": ["repositoryName"]},
    "codedeploy": {
        "GetDeploymentTarget": ["deploymentId"],
        "ListDeploymentTargets": ["deploymentId"],
    },
    "ecs": {
        "ListTasks": ["cluster"],
        "ListServices": ["cluster"],
        "ListContainerInstances": ["cluster"],
    },
    "elasticbeanstalk": {
        "DescribeEnvironmentHealth": ["environmentName"],
        "DescribeEnvironmentManagedActionHistory": ["environmentName"],
        "DescribeEnvironmentManagedActions": ["environmentName"],
        "DescribeEnvironmentResources": ["environmentName"],
        "DescribeInstancesHealth": ["environmentName"],
    },
    "iam": {
        "GetUser": ["userName"],
        "ListAccessKeys": ["userName"],
        "ListServiceSpecificCredentials": ["userName"],
        "ListSigningCertificates": ["userName"],
        "ListMFADevices": ["userName"],
        "ListSSHPublicKeys": ["userName"],
    },
    "iot": {"ListAuditFindings": ["taskId"]},
    "opsworks": {
        "ListAuditFindings": ["taskId"],
        "DescribeAgentVersions": ["stackId"],
        "DescribeApps": ["stackId"],
        "DescribeCommands": ["deploymentId"],
        "DescribeDeployments": ["appId"],
        "DescribeEcsClusters": ["ecsClusterArns"],
        "DescribeElasticIps": ["stackId"],
        "DescribeElasticLoadBalancers": ["stackId"],
        "DescribeInstances": ["stackId"],
        "DescribeLayers": ["stackId"],
        "DescribePermissions": ["stackId"],
        "DescribeRaidArrays": ["stackId"],
        "DescribeVolumes": ["stackId"],
    },
    "ssm": {"DescribeMaintenanceWindowSchedule": ["windowId"],},
    "shield": {"DescribeProtection": ["protectionId"],},
    "waf": {
        "ListActivatedRulesInRuleGroup": ["ruleGroupId"],
        "ListLoggingConfigurations": ["limit"],
    },
    "waf-regional": {
        "ListActivatedRulesInRuleGroup": ["ruleGroupId"],
        "ListLoggingConfigurations": ["limit"],
    },
    "wafv2": {"ListLoggingConfigurations": ["limit"],},
}

ON_TOP_POLICIES = [
    "kafka:ListClusters",
    "synthetics:DescribeCanaries",
    "medialive:ListInputs",
    "cloudhsm:DescribeClusters",
    "ssm:GetParametersByPath",
]

SKIPPED_SERVICES = [
    "sagemaker"
]  # those services have too unreliable API to make use of it

PARALLEL_SERVICE_CALLS = 80


def _to_snake_case(camel_case):
    return (
        re.sub("(?!^)([A-Z]+)", r"_\1", camel_case)
        .lower()
        .replace("open_idconnect", "open_id_connect")
        .replace("samlproviders", "saml_providers")
        .replace("sshpublic_keys", "ssh_public_keys")
        .replace("mfadevices", "mfa_devices")
        .replace("cacertificates", "ca_certificates")
        .replace("awsservice", "aws_service")
        .replace("dbinstances", "db_instances")
        .replace("drtaccess", "drt_access")
        .replace("ipsets", "ip_sets")
        .replace("mljobs", "ml_jobs")
        .replace("dbcluster", "db_cluster")
        .replace("dbengine", "db_engine")
        .replace("dbsecurity", "db_security")
        .replace("dbsubnet", "db_subnet")
        .replace("dbsnapshot", "db_snapshot")
        .replace("dbproxies", "db_proxies")
        .replace("dbparameter", "db_parameter")
        .replace("dbinstance", "db_instance")
        .replace("d_bparameter", "db_parameter")
        .replace("s_amlproviders", "saml_providers")
        .replace("a_wsservice", "aws_service")
    )


PLURAL_TO_SINGULAR = {
    "ies": "y",
    "status": "status",
    "ches": "ch",
    "ses": "s",
}


def singular_from_plural(name: str) -> str:
    if name.endswith("s"):
        for plural_suffix, singular_suffix in PLURAL_TO_SINGULAR.items():
            if name.endswith(plural_suffix):
                name = name[: -len(plural_suffix)] + singular_suffix
                return name
        if not name.endswith("ss"):
            name = name[:-1]
    return name


def last_singular_name_element(operation_name):
    last_name = re.findall("[A-Z][^A-Z]*", operation_name)[-1]
    return singular_from_plural(last_name)


def retrieve_resource_name(resource, operation_name):
    resource_name = None
    last_name = last_singular_name_element(operation_name)
    if "name" in resource:
        resource_name = resource["name"]
    elif "Name" in resource:
        resource_name = resource["Name"]
    elif last_name + "Name" in resource:
        resource_name = resource[last_name + "Name"]
    elif only_one_suffix(resource, "name"):
        resource_name = only_one_suffix(resource, "name")

    return resource_name


# pylint: disable=inconsistent-return-statements
def only_one_suffix(resource, suffix):
    id_keys = []
    last_id_val = None
    for key, val in resource.items():
        if key.lower().endswith(suffix) and not key.lower().endswith(
            "display" + suffix
        ):
            id_keys.append(key)
            last_id_val = val
    if len(id_keys) == 1:
        return last_id_val
    return None


def retrieve_resource_id(resource, operation_name, resource_name):
    resource_id = resource_name
    last_name = last_singular_name_element(operation_name)
    if "id" in resource:
        resource_id = resource["id"]
    elif last_name + "Id" in resource:
        resource_id = resource[last_name + "Id"]
    elif only_one_suffix(resource, "id"):
        resource_id = only_one_suffix(resource, "id")
    elif "arn" in resource:
        resource_id = resource["arn"]
    elif last_name + "Arn" in resource:
        resource_id = resource[last_name + "Arn"]
    elif only_one_suffix(resource, "arn"):
        resource_id = only_one_suffix(resource, "arn")

    return resource_id


def operation_allowed(
    allowed_actions: List[str], aws_service: str, operation_name: str
):
    evaluation_result = False
    for action in allowed_actions:
        if action == "*":
            evaluation_result = True
            break
        action_service = action.split(":", 1)[0]
        if not action_service == aws_service:
            continue
        action_operation = action.split(":", 1)[1]
        if action_operation.endswith("*") and operation_name.startswith(
            action_operation[:-1]
        ):
            evaluation_result = True
            break
        if operation_name == action_operation:
            evaluation_result = True
            break
    return evaluation_result


def build_resource(
    base_resource, operation_name, resource_type, group
) -> Optional[Resource]:
    if isinstance(base_resource, str):
        return None
    resource_name = retrieve_resource_name(base_resource, operation_name)
    resource_id = retrieve_resource_id(base_resource, operation_name, resource_name)

    if resource_id is None or resource_name is None:
        return None
    attributes = flatten(base_resource)
    return Resource(
        digest=ResourceDigest(id=resource_id, type=resource_type),
        group=group,
        name=resource_name,
        attributes=attributes,
        tags=resource_tags(base_resource),
    )


def all_exception(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        # pylint: disable=broad-except
        except Exception as e:
            if func.__qualname__ == "AllResources.analyze_operation":
                if not args[0].options.verbose:
                    return
                exception_str = str(e)
                if (
                    "is not subscribed to AWS Security Hub" in exception_str
                    or "not enabled for securityhub" in exception_str
                    or "The subscription does not exist" in exception_str
                    or "calling the DescribeHub operation" in exception_str
                ):
                    message_handler(
                        "Operation {} not accessible, AWS Security Hub is not configured... Skipping".format(
                            args[2]
                        ),
                        "WARNING",
                    )
                elif (
                    "not connect to the endpoint URL" in exception_str
                    or "not available in this region" in exception_str
                    or "API is not available" in exception_str
                ):
                    message_handler(
                        "Service {} not available in the selected region... Skipping".format(
                            args[5]
                        ),
                        "WARNING",
                    )
                elif (
                    "Your account is not a member of an organization" in exception_str
                    or "This action can only be made by accounts in an AWS Organization"
                    in exception_str
                    or "The request failed because organization is not in use"
                    in exception_str
                ):
                    message_handler(
                        "Service {} only available to account in an AWS Organization... Skipping".format(
                            args[5]
                        ),
                        "WARNING",
                    )
                elif "is no longer available to new customers" in exception_str:
                    message_handler(
                        "Service {} is no longer available to new customers... Skipping".format(
                            args[5]
                        ),
                        "WARNING",
                    )
                elif (
                    "only available to Master account in AWS FM" in exception_str
                    or "not currently delegated by AWS FM" in exception_str
                ):
                    message_handler(
                        "Operation {} not accessible, not master account in AWS FM... Skipping".format(
                            args[2]
                        ),
                        "WARNING",
                    )
                else:
                    log_critical(
                        "\nError running operation {}, type {}. Error message {}".format(
                            args[2], args[1], exception_str
                        )
                    )
            else:
                log_critical(
                    "\nError running method {}. Error message {}".format(
                        func.__qualname__, str(e)
                    )
                )

    return wrapper


def build_resource_type(aws_service, name):
    resource_name = re.sub(r"^List", "", name)
    resource_name = re.sub(r"^Get", "", resource_name)
    resource_name = re.sub(r"^Describe", "", resource_name)
    return singular_from_plural(
        "aws_{}_{}".format(
            aws_service.replace("-", "_"), _to_snake_case(resource_name),
        )
    )


def flatten(d, parent_key="", sep="."):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


class AllResources(ResourceProvider):
    def __init__(self, options: AllOptions):
        """
        All resources

        :param options:
        """
        super().__init__()
        self.options = options
        self.availabilityCheck = ResourceAvailable("")

    @all_exception
    def get_resources(self) -> List[Resource]:
        boto_loader = Loader()
        if self.options.services:
            aws_services = self.options.services
        else:
            aws_services = boto_loader.list_available_services(type_name="service-2")
        resources = []
        allowed_actions = self.get_policies_allowed_actions()

        if self.options.verbose:
            message_handler(
                "Analyzing listing operations across {} service...".format(
                    len(aws_services)
                ),
                "HEADER",
            )
        with ThreadPoolExecutor(PARALLEL_SERVICE_CALLS) as executor:
            results = executor.map(
                lambda aws_service: self.analyze_service(
                    aws_service, boto_loader, allowed_actions
                ),
                aws_services,
            )
        for service_resources in results:
            if service_resources is not None:
                resources.extend(service_resources)

        return resources

    @all_exception
    def analyze_service(self, aws_service, boto_loader, allowed_actions):
        resources = []
        client = self.options.client(aws_service)
        service_model = boto_loader.load_service_model(aws_service, "service-2")
        try:
            paginators_model = boto_loader.load_service_model(
                aws_service, "paginators-1"
            )
        except UnknownServiceError:
            paginators_model = {"pagination": {}}
        service_full_name = service_model["metadata"]["serviceFullName"]
        if self.options.verbose:
            message_handler(
                "Collecting data from {}...".format(service_full_name), "HEADER"
            )
        if (
            not self.availabilityCheck.is_service_available(
                self.options.region_name, aws_service
            )
            or aws_service in SKIPPED_SERVICES
        ) and self.options.verbose:
            message_handler(
                "Service {} not available in this region... Skipping".format(
                    service_full_name
                ),
                "WARNING",
            )
            return None
        for name, operation in service_model["operations"].items():
            if (
                name.startswith("List")
                or name.startswith("Get")
                or name.startswith("Describe")
            ):
                has_paginator = name in paginators_model["pagination"]
                if "input" in operation:
                    input_model = service_model["shapes"][operation["input"]["shape"]]
                    if "required" in input_model and input_model["required"]:
                        continue
                    if (
                        aws_service in REQUIRED_PARAMS_OVERRIDE
                        and operation["name"] in REQUIRED_PARAMS_OVERRIDE[aws_service]
                    ):
                        continue
                resource_type = build_resource_type(aws_service, name)
                if resource_type in OMITTED_RESOURCES:
                    continue
                if not operation_allowed(allowed_actions, aws_service, name):
                    continue
                analyze_operation = self.analyze_operation(
                    resource_type,
                    name,
                    has_paginator,
                    client,
                    service_full_name,
                    aws_service,
                )
                if analyze_operation is not None:
                    resources.extend(analyze_operation)
        return resources

    @all_exception
    # pylint: disable=too-many-locals,too-many-arguments
    def analyze_operation(
        self,
        resource_type,
        operation_name,
        has_paginator,
        client,
        service_full_name,
        aws_service,
    ) -> List[Resource]:
        resources = []
        snake_operation_name = _to_snake_case(operation_name)
        # pylint: disable=too-many-nested-blocks
        if has_paginator:
            pages = get_paginator(
                client=client,
                operation_name=snake_operation_name,
                resource_type=resource_type,
                filters=None,
            )
            list_metadata = pages.result_keys[0].parsed
            result_key = None
            result_parent = None
            result_child = None
            if "value" in list_metadata:
                result_key = list_metadata["value"]
            elif "type" in list_metadata and list_metadata["type"] == "subexpression":
                result_parent = list_metadata["children"][0]["value"]
                result_child = list_metadata["children"][1]["value"]
            else:
                if self.options.verbose:
                    message_handler(
                        "Operation {} has unsupported pagination definition... Skipping".format(
                            snake_operation_name
                        ),
                        "WARNING",
                    )
                return []
            for page in pages:
                if result_key == "Reservations":  # hack for EC2 instances
                    for page_reservation in page["Reservations"]:
                        for instance in page_reservation["Instances"]:
                            resource = build_resource(
                                instance, operation_name, resource_type, aws_service
                            )
                            if resource is not None:
                                resources.append(resource)
                if result_key is not None:
                    page_resources = page[result_key]
                elif result_child in page[result_parent]:
                    page_resources = page[result_parent][result_child]
                else:
                    page_resources = []
                for page_resource in page_resources:
                    resource = build_resource(
                        page_resource, operation_name, resource_type, aws_service
                    )
                    if resource is not None:
                        resources.append(resource)
        else:

            response = getattr(client, snake_operation_name)()
            for response_elem in response.values():
                if isinstance(response_elem, list):
                    for response_resource in response_elem:
                        resource = build_resource(
                            response_resource,
                            operation_name,
                            resource_type,
                            aws_service,
                        )
                        if resource is not None:
                            resources.append(resource)
        return resources

    def get_policies_allowed_actions(self):
        if self.options.verbose:
            message_handler("Fetching allowed actions...", "HEADER")
        iam_client = self.options.client("iam")
        view_only_document = self.get_policy_allowed_calls(
            iam_client, "arn:aws:iam::aws:policy/job-function/ViewOnlyAccess"
        )
        sec_audit_document = self.get_policy_allowed_calls(
            iam_client, "arn:aws:iam::aws:policy/SecurityAudit"
        )

        allowed_actions = {}
        for action in view_only_document["Statement"][0]["Action"]:
            allowed_actions[action] = True
        for action in sec_audit_document["Statement"][0]["Action"]:
            allowed_actions[action] = True
        for action in ON_TOP_POLICIES:
            allowed_actions[action] = True
        if self.options.verbose:
            message_handler(
                "Found {} allowed actions".format(len(allowed_actions)), "HEADER"
            )

        return allowed_actions.keys()

    def get_policy_allowed_calls(self, iam_client, policy_arn):
        policy_version_id = iam_client.get_policy(PolicyArn=policy_arn)["Policy"][
            "DefaultVersionId"
        ]
        policy_document = iam_client.get_policy_version(
            PolicyArn=policy_arn, VersionId=policy_version_id
        )["PolicyVersion"]["Document"]

        return policy_document
