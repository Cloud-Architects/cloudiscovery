import collections
import itertools
import re
from concurrent.futures.thread import ThreadPoolExecutor
from typing import List, Optional

from botocore.exceptions import UnknownServiceError
from botocore.loaders import Loader

from provider.all.command import AllOptions
from provider.all.data.omitted_resources import OMITTED_RESOURCES
from provider.all.data.on_top_policies import ON_TOP_POLICIES
from provider.all.data.required_params_override import REQUIRED_PARAMS_OVERRIDE
from provider.all.exception import all_exception
from shared.common import (
    ResourceProvider,
    Resource,
    ResourceDigest,
    message_handler,
    ResourceAvailable,
)
from shared.common_aws import get_paginator, resource_tags

SKIPPED_SERVICES = [
    "sagemaker"
]  # those services have too unreliable API to make use of it

PARALLEL_SERVICE_CALLS = 80

PLURAL_TO_SINGULAR = {
    "ies": "y",
    "status": "status",
    "ches": "ch",
    "ses": "s",
}

LISTING_PREFIXES = ["List", "Get", "Describe"]


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


def singular_from_plural(name: str) -> str:
    if name.endswith("s"):
        for plural_suffix, singular_suffix in PLURAL_TO_SINGULAR.items():
            if name.endswith(plural_suffix):
                name = name[: -len(plural_suffix)] + singular_suffix
                return name
        if not name.endswith("ss"):
            name = name[:-1]
    return name


def is_listing_operation(operation_name: str) -> bool:
    return (
        operation_name.startswith("List")
        or operation_name.startswith("Get")
        or operation_name.startswith("Describe")
    )


def last_singular_name_element(operation_name):
    last_name = re.findall("[A-Z][^A-Z]*", operation_name)[-1]
    return singular_from_plural(last_name)


def retrieve_resource_name(resource, operation_name):
    resource_name = None
    last_name = last_singular_name_element(operation_name)
    if isinstance(resource, str):
        resource_name = resource
    elif "name" in resource:
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
        if key.lower().endswith(suffix.lower()) and not key.lower().endswith(
            "display" + suffix.lower()
        ):
            id_keys.append(key)
            last_id_val = val
    if len(id_keys) == 1:
        return last_id_val
    return None


def retrieve_resource_id(resource, operation_name, resource_name):
    resource_id = resource_name
    last_name = last_singular_name_element(operation_name)
    if isinstance(resource, str):
        resource_id = resource
    elif "id" in resource:
        resource_id = resource["id"]
    elif last_name + "Id" in resource:
        resource_id = resource[last_name + "Id"]
    elif only_one_suffix(resource, "id"):
        resource_id = only_one_suffix(resource, "id")
    elif "arn" in resource:
        resource_id = resource["arn"]
    elif only_one_suffix(resource, last_name + "arn"):
        resource_id = only_one_suffix(resource, last_name + "arn")
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
    resource_name = retrieve_resource_name(base_resource, operation_name)
    resource_id = retrieve_resource_id(base_resource, operation_name, resource_name)

    if resource_name is None and resource_id is not None:
        resource_name = resource_id

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
    if isinstance(d, str):
        return {}
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def operation_required_fields(aws_service, input_model, operation):
    required_fields = []
    if "required" in input_model and input_model["required"]:
        required_fields = input_model["required"]
    if (
        aws_service in REQUIRED_PARAMS_OVERRIDE
        and operation["name"] in REQUIRED_PARAMS_OVERRIDE[aws_service]
    ):
        required_fields = REQUIRED_PARAMS_OVERRIDE[aws_service][operation["name"]]
    return required_fields


def get_policy_allowed_calls(iam_client, policy_arn):
    policy_version_id = iam_client.get_policy(PolicyArn=policy_arn)["Policy"][
        "DefaultVersionId"
    ]
    policy_document = iam_client.get_policy_version(
        PolicyArn=policy_arn, VersionId=policy_version_id
    )["PolicyVersion"]["Document"]

    return policy_document


def permutate_parameters(operation_parameters):
    if not operation_parameters:
        return {}
    operation_parameter_keys, operation_parameter_values = zip(
        *operation_parameters.items()
    )
    parameters_permutation = [
        dict(zip(operation_parameter_keys, v))
        for v in itertools.product(*operation_parameter_values)
    ]
    return parameters_permutation


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

    # pylint: disable=too-many-locals
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
            if is_listing_operation(name):
                has_paginator = name in paginators_model["pagination"]
                resource_type = build_resource_type(aws_service, name)
                if resource_type in OMITTED_RESOURCES:
                    continue
                if not operation_allowed(allowed_actions, aws_service, name):
                    continue

                operation_parameters = dict()
                if "input" in operation:
                    input_model = service_model["shapes"][operation["input"]["shape"]]
                    required_fields = operation_required_fields(
                        aws_service, input_model, operation
                    )

                    if len(required_fields) == 1:
                        required_field = required_fields[0]
                        required_field_values = self.check_required_field(
                            required_field,
                            service_model,
                            paginators_model["pagination"],
                            aws_service,
                            allowed_actions,
                            client,
                            service_full_name,
                        )
                        operation_parameters[required_field] = required_field_values
                    elif len(required_fields) != 0:
                        continue

                parameters_permutation = permutate_parameters(operation_parameters)

                for parameter_permutation in parameters_permutation:
                    operation_resources = self.retrieve_operation_resources(
                        resource_type,
                        name,
                        has_paginator,
                        client,
                        service_full_name,
                        aws_service,
                        parameter_permutation,
                    )
                    if operation_resources is not None:
                        resources.extend(operation_resources)
        return resources

    @all_exception
    # pylint: disable=too-many-locals,too-many-arguments
    def retrieve_operation_resources(
        self,
        resource_type,
        operation_name,
        has_paginator,
        client,
        service_full_name,
        aws_service,
        operation_parameters=None,
    ) -> List[Resource]:
        if operation_parameters is None:
            operation_parameters = {}
        resources = []
        snake_operation_name = _to_snake_case(operation_name)
        # pylint: disable=too-many-nested-blocks
        if has_paginator:
            pages = get_paginator(
                client=client,
                operation_name=snake_operation_name,
                resource_type=resource_type,
                filters=operation_parameters,
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
            response = getattr(client, snake_operation_name)(**operation_parameters)
            for response_field, response_elem in response.items():
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
                elif response_field != "ResponseMetadata":
                    resource = build_resource(
                        response_elem, operation_name, resource_type, aws_service,
                    )
                    if resource is not None:
                        resources.append(resource)
        return resources

    def get_policies_allowed_actions(self):
        if self.options.verbose:
            message_handler("Fetching allowed actions...", "HEADER")
        iam_client = self.options.client("iam")
        view_only_document = get_policy_allowed_calls(
            iam_client, "arn:aws:iam::aws:policy/job-function/ViewOnlyAccess"
        )
        sec_audit_document = get_policy_allowed_calls(
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

    # pylint: disable=too-many-arguments
    def check_required_field(
        self,
        required_field,
        service_model,
        pagination_model,
        aws_service,
        allowed_actions,
        client,
        service_full_name,
    ):
        method = None
        operation = None
        for operation_name, service_operation in service_model["operations"].items():
            if operation_name.lower().startswith("list" + required_field[:-1].lower()):
                method = operation_name
                operation = service_operation
        if method is None:
            return []

        has_paginator = method in pagination_model
        resource_type = build_resource_type(aws_service, method)
        if resource_type in OMITTED_RESOURCES:
            return []
        if not operation_allowed(allowed_actions, aws_service, method):
            return []

        if "input" in operation:
            input_model = service_model["shapes"][operation["input"]["shape"]]
            required_fields = operation_required_fields(
                aws_service, input_model, operation
            )
            if required_fields:
                return []

        operation_resources = self.retrieve_operation_resources(
            resource_type,
            method,
            has_paginator,
            client,
            service_full_name,
            aws_service,
        )
        required_field_ids = []

        for resource in operation_resources:
            required_field_ids.append(resource.digest.id)

        return required_field_ids
