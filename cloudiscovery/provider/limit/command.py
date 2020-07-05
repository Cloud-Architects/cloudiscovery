from typing import List

from shared.common import ResourceCache, message_handler, Filterable, BaseOptions
from shared.common_aws import BaseAwsOptions, BaseAwsCommand, AwsCommandRunner
from shared.diagram import NoDiagram

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
    "appmesh": {
        "L-AC861A39": {"method": "list_meshes", "key": "meshes", "fields": [],},
        "global": False,
    },
    "appsync": {
        "L-06A0647C": {
            "method": "list_graphql_apis",
            "key": "graphqlApis",
            "fields": [],
        },
        "global": False,
    },
    "autoscaling-plans": {
        "L-BD401546": {
            "method": "describe_scaling_plans",
            "key": "ScalingPlans",
            "fields": [],
        },
        "global": False,
    },
    "batch": {
        "L-144F0CA5": {
            "method": "describe_compute_environments",
            "key": "computeEnvironments",
            "fields": [],
        },
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
        "L-0485CB21": {
            "method": "list_stacks",
            "key": "StackSummaries",
            "fields": [],
            "filter": {
                "StackStatusFilter": [
                    "CREATE_IN_PROGRESS",
                    "CREATE_FAILED",
                    "CREATE_COMPLETE",
                    "ROLLBACK_IN_PROGRESS",
                    "ROLLBACK_FAILED",
                    "ROLLBACK_COMPLETE",
                    "DELETE_IN_PROGRESS",
                    "DELETE_FAILED",
                    "UPDATE_IN_PROGRESS",
                    "UPDATE_COMPLETE_CLEANUP_IN_PROGRESS",
                    "UPDATE_COMPLETE",
                    "UPDATE_ROLLBACK_IN_PROGRESS",
                    "UPDATE_ROLLBACK_FAILED",
                    "UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS",
                    "UPDATE_ROLLBACK_COMPLETE",
                    "REVIEW_IN_PROGRESS",
                    "IMPORT_IN_PROGRESS",
                    "IMPORT_COMPLETE",
                    "IMPORT_ROLLBACK_IN_PROGRESS",
                    "IMPORT_ROLLBACK_FAILED",
                    "IMPORT_ROLLBACK_COMPLETE",
                ]
            },
        },
        "L-9DE8E4FB": {"method": "list_types", "key": "TypeSummaries", "fields": [],},
        "global": False,
    },
    "codeguru-reviewer": {
        "L-F5129FC6": {
            "method": "list_code_reviews",
            "key": "CodeReviewSummaries",
            "fields": [],
            "filter": {"Type": "PullRequest"},
        },
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
    "vpc": {
        "L-F678F1CE": {"method": "describe_vpcs", "key": "Vpcs", "fields": [],},
        "global": False,
    },
}


class LimitOptions(BaseAwsOptions, BaseOptions):
    services: List[str]
    threshold: str

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        verbose: bool,
        filters: List[Filterable],
        session,
        region_name,
        services,
        threshold,
    ):
        BaseAwsOptions.__init__(self, session, region_name)
        BaseOptions.__init__(self, verbose, filters)
        self.services = services
        self.threshold = threshold


class LimitParameters:
    def __init__(self, session, region: str, services):
        self.region = region
        self.cache = ResourceCache()
        self.session = session
        self.services = []
        if services is None:
            for service in ALLOWED_SERVICES_CODES:
                self.services.append(service)
        else:
            self.services = services

    def init_globalaws_limits_cache(self):
        """
        AWS has global limit that can be adjustable and others that can't be adjustable
        This method make cache for 15 days for aws cache global parameters. AWS don't update limit every time.
        Services has differents limit, depending on region.
        """
        for service_code in self.services:
            if service_code in ALLOWED_SERVICES_CODES:
                cache_key = "aws_limits_" + service_code + "_" + self.region

                cache = self.cache.get_key(cache_key)
                if cache is not None:
                    continue

                message_handler(
                    "Fetching aws global limit to service {} in region {} to cache...".format(
                        service_code, self.region
                    ),
                    "HEADER",
                )

                cache_codes = dict()
                for quota_code in ALLOWED_SERVICES_CODES[service_code]:

                    if quota_code != "global":
                        """
                        Impossible to instance once at __init__ method.
                        Global services such route53 MUST USE us-east-1 region
                        """
                        if ALLOWED_SERVICES_CODES[service_code]["global"]:
                            service_quota = self.session.client(
                                "service-quotas", region_name="us-east-1"
                            )
                        else:
                            service_quota = self.session.client(
                                "service-quotas", region_name=self.region
                            )

                        response = service_quota.get_aws_default_service_quota(
                            ServiceCode=service_code, QuotaCode=quota_code
                        )

                        item_to_add = {
                            "value": response["Quota"]["Value"],
                            "adjustable": response["Quota"]["Adjustable"],
                            "quota_code": quota_code,
                            "quota_name": response["Quota"]["QuotaName"],
                        }

                        if service_code in cache_codes:
                            cache_codes[service_code].append(item_to_add)
                        else:
                            cache_codes[service_code] = [item_to_add]

                self.cache.set_key(key=cache_key, value=cache_codes, expire=1296000)

        return True


class Limit(BaseAwsCommand):
    def __init__(self, region_names, session, threshold):
        """
        All AWS resources

        :param region_names:
        :param session:
        :param threshold:
        """
        super().__init__(region_names, session)
        self.threshold = threshold

    def init_globalaws_limits_cache(self, region, services):
        # Cache services global and local services
        LimitParameters(
            session=self.session, region=region, services=services
        ).init_globalaws_limits_cache()

    def run(
        self,
        diagram: bool,
        verbose: bool,
        services: List[str],
        filters: List[Filterable],
    ):
        if not services:
            services = []
            for service in ALLOWED_SERVICES_CODES:
                services.append(service)

        for region in self.region_names:
            self.init_globalaws_limits_cache(region=region, services=services)
            limit_options = LimitOptions(
                verbose=verbose,
                filters=filters,
                session=self.session,
                region_name=region,
                services=services,
                threshold=self.threshold,
            )

            command_runner = AwsCommandRunner(services=services)
            command_runner.run(
                provider="limit",
                options=limit_options,
                diagram_builder=NoDiagram(),
                title="AWS Limits - Region {}".format(region),
                # pylint: disable=no-member
                filename=limit_options.resulting_file_name("limit"),
            )
