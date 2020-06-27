import re
from concurrent.futures.thread import ThreadPoolExecutor
from functools import reduce
from typing import List

from botocore.loaders import Loader

from shared.common import (
    ResourceProvider,
    Resource,
    BaseAwsOptions,
    ResourceDigest,
    message_handler,
    ResourceAvailable,
)
from shared.error_handler import exception

OMITTED_RESOURCES = [
    "aws_dax_default_parameter",
    "aws_dax_parameter_group",
    "aws_ec2_reserved_instances_offering",
    "aws_ec2_snapshot",
    "aws_ec2_spot_price_history",
    "aws_ssm_available_patche",
    "aws_ssm_document",
    "aws_polly_voice",
    "aws_lightsail_blueprint",
    "aws_lightsail_bundle",
    "aws_elastictranscoder_preset",
    "aws_ec2_vpc_endpoint_service",
    "aws_dms_endpoint_type",
    "aws_elasticache_service_update",
    "aws_elasticache_cache_parameter_group",
    "aws_rds_source_region",
    "aws_ssm_association",
    "aws_ssm_patch_baseline",
]

ON_TOP_POLICIES = [
    "kafka:ListClusters",
    "synthetics:DescribeCanaries",
    "medialive:ListInputs",
    "cloudhsm:DescribeClusters",
    "ssm:GetParametersByPath",
]


def _to_snake_case(function):
    return reduce(lambda x, y: x + ("_" if y.isupper() else "") + y, function).lower()


def last_singular_name_element(operation_name):
    last_name = re.findall("[A-Z][^A-Z]*", operation_name)[-1]
    if last_name.endswith("s"):
        last_name = last_name[:-1]
    return last_name


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
    # type 'aws_ec2_dhcp_option'
    # 'DhcpOptionsId' -> 'dopt-042d18a4769f7b35b'
    # also got 'OwnerId'

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


class AllResources(ResourceProvider):
    def __init__(self, options: BaseAwsOptions):
        """
        All resources

        :param options:
        """
        super().__init__()
        self.options = options
        self.availabilityCheck = ResourceAvailable("")

    @exception
    def get_resources(self) -> List[Resource]:
        boto_loader = Loader()
        aws_services = boto_loader.list_available_services(type_name="service-2")
        resources = []
        allowed_actions = self.get_policies_allowed_actions()

        with ThreadPoolExecutor(80) as executor:
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

    @exception
    def analyze_service(self, aws_service, boto_loader, allowed_actions):
        resources = []
        client = self.options.client(aws_service)
        service_model = boto_loader.load_service_model(aws_service, "service-2")
        paginators_model = boto_loader.load_service_model(aws_service, "paginators-1")
        service_full_name = service_model["metadata"]["serviceFullName"]
        message_handler(
            "Collecting data from {}...".format(service_full_name), "HEADER"
        )
        if not self.availabilityCheck.is_service_available(
            self.options.region_name, aws_service
        ):
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
                input_model = service_model["shapes"][operation["input"]["shape"]]
                if "required" in input_model and input_model["required"]:
                    continue
                resource_type = "aws_{}_{}".format(
                    aws_service,
                    _to_snake_case(
                        name.replace("List", "")
                        .replace("Get", "")
                        .replace("Describe", "")
                    ),
                )
                if resource_type.endswith("s"):
                    resource_type = resource_type[:-1]
                if resource_type in OMITTED_RESOURCES:
                    continue
                if not operation_allowed(allowed_actions, aws_service, name):
                    continue
                analyze_operation = self.analyze_operation(
                    resource_type, name, has_paginator, client
                )
                if analyze_operation is not None:
                    resources.extend(analyze_operation)
        return resources

    @exception
    def analyze_operation(
        self, resource_type, operation_name, has_paginator, client
    ) -> List[Resource]:
        resources = []
        if has_paginator:
            paginator = client.get_paginator(_to_snake_case(operation_name))
            pages = paginator.paginate()
            result_key = pages.result_keys[0].parsed["value"]
            for page in pages:
                for resource in page[result_key]:
                    if isinstance(resource, str):
                        continue

                    resource_name = retrieve_resource_name(resource, operation_name)
                    resource_id = retrieve_resource_id(
                        resource, operation_name, resource_name
                    )

                    if resource_id is None or resource_name is None:
                        continue

                    resources.append(
                        Resource(
                            digest=ResourceDigest(id=resource_id, type=resource_type),
                            name=resource_name,
                        )
                    )
        return resources

    def get_policies_allowed_actions(self):
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
