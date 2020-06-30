from typing import List

from concurrent.futures.thread import ThreadPoolExecutor

from shared.common import get_paginator

from shared.common import (
    ResourceProvider,
    Resource,
    BaseAwsOptions,
    ResourceDigest,
    message_handler,
    ResourceCache,
    LimitsValues,
)
from shared.error_handler import exception

ALLOWED_SERVICES_CODES = {
    "acm": {
        "L-F141DD1D": {
            "method": "list_certificates",
            "key": "CertificateSummaryList",
            "fields": [],
        },
        "global": False,
    },
    "amplify": {
        "L-1BED97F3": {"method": "list_apps", "key": "apps", "fields": [],},
        "global": False,
    },
    "codebuild": {
        "L-ACCF6C0D": {"method": "list_projects", "key": "projects", "fields": [],},
        "global": False,
    },
    "codecommit": {
        "L-81790602": {
            "method": "list_repositories",
            "key": "repositories",
            "fields": [],
        },
        "global": False,
    },
    "cloudformation": {
        "L-0485CB21": {"method": "list_stacks", "key": "StackSummaries", "fields": [],},
        "L-9DE8E4FB": {"method": "list_types", "key": "TypeSummaries", "fields": [],},
        "global": False,
    },
    "dynamodb": {
        "L-F98FE922": {"method": "list_tables", "key": "TableNames", "fields": [],},
        "global": False,
    },
    "ec2": {
        "L-0263D0A3": {
            "method": "describe_addresses",
            "key": "Addresses",
            "fields": [],
        },
        "global": False,
    },
    "ecs": {
        "L-21C621EB": {"method": "list_clusters", "key": "clusterArns", "fields": [],},
        "global": False,
    },
    "elasticfilesystem": {
        "L-848C634D": {
            "method": "describe_file_systems",
            "key": "FileSystems",
            "fields": [],
        },
        "global": False,
    },
    "elasticbeanstalk": {
        "L-8EFC1C51": {
            "method": "describe_environments",
            "key": "Environments",
            "fields": [],
        },
        "L-1CEABD17": {
            "method": "describe_applications",
            "key": "Applications",
            "fields": [],
        },
        "global": False,
    },
    "elasticloadbalancing": {
        "L-53DA6B97": {
            "method": "describe_load_balancers",
            "key": "LoadBalancers",
            "fields": [],
        },
        "global": False,
    },
    "iam": {
        "L-F4A5425F": {"method": "list_groups", "key": "Groups", "fields": [],},
        "L-F55AF5E4": {"method": "list_users", "key": "Users", "fields": [],},
        "L-BF35879D": {
            "method": "list_server_certificates",
            "key": "ServerCertificateMetadataList",
            "fields": [],
        },
        "L-6E65F664": {
            "method": "list_instance_profiles",
            "key": "InstanceProfiles",
            "fields": [],
            "paginate": False,
        },
        "L-FE177D64": {"method": "list_roles", "key": "Roles", "fields": [],},
        "L-DB618D39": {
            "method": "list_saml_providers",
            "key": "SAMLProviderList",
            "fields": [],
        },
        "global": True,
    },
    "kms": {
        "L-C2F1777E": {"method": "list_keys", "key": "Keys", "fields": [],},
        "global": False,
    },
    "mediaconnect": {
        "L-A99016A8": {"method": "list_flows", "key": "Flows", "fields": [],},
        "L-F1F62F5D": {
            "method": "list_entitlements",
            "key": "Entitlements",
            "fields": [],
        },
        "global": False,
    },
    "medialive": {
        "L-D1AFAF75": {"method": "list_channels", "key": "Channels", "fields": [],},
        "L-BDF24E14": {
            "method": "list_input_devices",
            "key": "InputDevices",
            "fields": [],
        },
        "global": False,
    },
    "mediapackage": {
        "L-352B8598": {"method": "list_channels", "key": "Channels", "fields": [],},
        "global": False,
    },
    "qldb": {
        "L-CD70CADB": {"method": "list_ledgers", "key": "Ledgers", "fields": [],},
        "global": False,
    },
    "robomaker": {
        "L-40FACCBF": {"method": "list_robots", "key": "robots", "fields": [],},
        "L-D6554FB1": {
            "method": "list_simulation_applications",
            "key": "simulationApplicationSummaries",
            "fields": [],
        },
        "global": False,
    },
    "route53": {
        "L-4EA4796A": {
            "method": "list_hosted_zones",
            "key": "HostedZones",
            "fields": [],
        },
        "L-ACB674F3": {
            "method": "list_health_checks",
            "key": "HealthChecks",
            "fields": [],
        },
        "global": True,
    },
    "route53resolver": {
        "L-4A669CC0": {
            "method": "list_resolver_endpoints",
            "key": "ResolverEndpoints",
            "fields": [],
        },
        "L-51D8A1FB": {
            "method": "list_resolver_rules",
            "key": "ResolverRules",
            "fields": [],
        },
        "global": True,
    },
    "rds": {
        "L-7B6409FD": {
            "method": "describe_db_instances",
            "key": "DBInstances",
            "fields": [],
        },
        "L-952B80B8": {
            "method": "describe_db_clusters",
            "key": "DBClusters",
            "fields": [],
        },
        "L-DE55804A": {
            "method": "describe_db_parameter_groups",
            "key": "DBParameterGroups",
            "fields": [],
        },
        "L-9FA33840": {
            "method": "describe_option_groups",
            "key": "OptionGroupsList",
            "fields": [],
        },
        "global": False,
    },
    "s3": {
        "L-DC2B2D3D": {"method": "list_buckets", "key": "Buckets", "fields": [],},
        "global": False,
    },
    "sns": {
        "L-61103206": {"method": "list_topics", "key": "Topics", "fields": [],},
        "global": False,
    },
    "transcribe": {
        "L-3278D334": {
            "method": "list_vocabularies",
            "key": "Vocabularies",
            "fields": [],
        },
        "global": False,
    },
    "translate": {
        "L-4011ABD8": {
            "method": "list_terminologies",
            "key": "TerminologyPropertiesList",
            "fields": [],
        },
        "global": False,
    },
}

SERVICEQUOTA_TO_BOTO3 = {
    "elasticloadbalancing": "elbv2",
    "elasticfilesystem": "efs",
}

MAX_EXECUTION_PARALLEL = 3


class LimitResources(ResourceProvider):
    def __init__(self, options: BaseAwsOptions):
        """
        All resources

        :param options:
        """
        super().__init__()
        self.options = options
        self.cache = ResourceCache()

    @exception
    # pylint: disable=too-many-locals
    def get_resources(self) -> List[Resource]:

        usage_check = 0 if self.options.usage is None else self.options.usage

        client_quota = self.options.session.client("service-quotas")

        resources_found = []

        services = self.options.services

        with ThreadPoolExecutor(MAX_EXECUTION_PARALLEL) as executor:
            results = executor.map(
                lambda aws_limit: self.analyze_service(
                    aws_limit=aws_limit,
                    client_quota=client_quota,
                    usage_check=int(usage_check),
                ),
                services,
            )

        for result in results:
            if result is not None:
                resources_found.extend(result)

        return resources_found

    @exception
    def analyze_service(self, aws_limit, client_quota, usage_check):

        service = aws_limit

        cache_key = "aws_limits_" + service + "_" + self.options.region_name
        cache = self.cache.get_key(cache_key)

        return self.analyze_detail(
            client_quota=client_quota,
            data_resource=cache[service],
            service=service,
            usage_check=usage_check,
        )

    @exception
    # pylint: disable=too-many-locals
    def analyze_detail(self, client_quota, data_resource, service, usage_check):

        resources_found = []

        for data_quota_code in data_resource:

            quota_data = ALLOWED_SERVICES_CODES[service][data_quota_code["quota_code"]]

            value_aws = value = data_quota_code["value"]

            # Quota is adjustable by ticket request, then must override this values.
            if bool(data_quota_code["adjustable"]) is True:
                try:
                    response_quota = client_quota.get_service_quota(
                        ServiceCode=service, QuotaCode=data_quota_code["quota_code"]
                    )
                    if "Value" in response_quota["Quota"]:
                        value = response_quota["Quota"]["Value"]
                    else:
                        value = data_quota_code["value"]
                except client_quota.exceptions.NoSuchResourceException:
                    value = data_quota_code["value"]

            message_handler(
                "Collecting data from Quota: "
                + service
                + " - "
                + data_quota_code["quota_name"]
                + "...",
                "HEADER",
            )

            # Need to convert some quota-services endpoint
            if service in SERVICEQUOTA_TO_BOTO3:
                service = SERVICEQUOTA_TO_BOTO3.get(service)

            client = self.options.session.client(
                service, region_name=self.options.region_name
            )

            usage = 0

            pages = get_paginator(
                client=client,
                operation_name=quota_data["method"],
                resource_type="aws_limit",
            )
            if not pages:
                response = getattr(client, quota_data["method"])()
                usage = len(response[quota_data["key"]])
            else:
                for page in pages:
                    usage = usage + len(page[quota_data["key"]])

            percent = round((usage / value) * 100, 2)

            if percent >= usage_check:
                resources_found.append(
                    Resource(
                        digest=ResourceDigest(
                            id=data_quota_code["quota_code"], type="aws_limit"
                        ),
                        name="",
                        group="",
                        limits=LimitsValues(
                            quota_name=data_quota_code["quota_name"],
                            quota_code=data_quota_code["quota_code"],
                            aws_limit=int(value_aws),
                            local_limit=int(value),
                            usage=int(usage),
                            service=service,
                            percent=percent,
                        ),
                    )
                )

        return resources_found
