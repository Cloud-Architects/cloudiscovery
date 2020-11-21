"""
JSON Format to check quota

    "service": {
        "quota-code": {
            "method": "xxx",
            "key": "xxx",
            "fields": "xxx",
            "divisor": xxx,
            "filter": {xxx},
        },
        "global": True|False,
    }

service:
    - Service name in Services Quota
    - Ref: https://docs.aws.amazon.com/cli/latest/reference/service-quotas/list-service-quotas.html

quota-code:
    - Quota code used by Services Quota
    - Ref: https://docs.aws.amazon.com/cli/latest/reference/service-quotas/list-service-quotas.html

method:
    - boto3 method name to check a specific resource. Usually List*, Describe*, Get*
    - Ref: https://boto3.amazonaws.com/v1/documentation/api/latest/index.html
    - Example:
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_volumes

key:
    - boto3 key List

fields:
    - If needed sum a specific field, specify here

divisor:
    - If used fields and needs to convert between TB -> GB, GB -> TB, GB -> MB, others.

filter:
    - Filter format used by boto3 resource. Check boto3 documentation
    - Example: "filter": {"Filters": [{"Name": "", "Values": [],}]},
    - Example: "filter": {"Type": "PullRequest"},

global:
    - Global parameter determines if this is an AWS Global Service such IAM, Route53, others.
"""

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
    "apigateway": {
        "L-1D180A63": {"method": "get_api_keys", "key": "items", "fields": [],},
        "L-824C9E42": {
            "method": "get_client_certificates",
            "key": "items",
            "fields": [],
        },
        "L-A93447B8": {"method": "get_domain_names", "key": "items", "fields": [],},
        "L-E8693075": {"method": "get_usage_plans", "key": "items", "fields": [],},
        "L-A4C7274F": {"method": "get_vpc_links", "key": "items", "fields": [],},
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
    "AWSCloudMap": {
        "L-0FE3F50E": {"method": "list_namespaces", "key": "Namespaces", "fields": [],},
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
    "chime": {
        "L-8EE806B4": {
            "method": "list_voice_connectors",
            "key": "VoiceConnectors",
            "fields": [],
        },
        "L-32405DBA": {
            "method": "list_phone_numbers",
            "key": "PhoneNumbers",
            "fields": [],
        },
        "L-D3615084": {
            "method": "list_voice_connector_groups",
            "key": "VoiceConnectorGroups",
            "fields": [],
        },
        "global": True,
    },
    "codeartifact": {
        "L-DD7208D3": {"method": "list_domains", "key": "domains", "fields": [],},
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
    "codedeploy": {
        "L-3F19B6A5": {
            "method": "list_applications",
            "key": "applications",
            "fields": [],
        },
        "L-B0CB7B38": {
            "method": "list_git_hub_account_token_names",
            "key": "tokenNameList",
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
        "L-31709F13": {"method": "list_stack_sets", "key": "Summaries", "fields": [],},
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
    "codeguru-profiler": {
        "L-DA8D4E8D": {
            "method": "list_profiling_groups",
            "key": "profilingGroupNames",
            "fields": [],
        },
        "global": False,
    },
    "cognito-identity": {
        "L-8692CE1C": {
            "method": "list_identity_pools",
            "key": "IdentityPools",
            "fields": [],
            "filter": {"MaxResults": 60},
        },
        "global": False,
    },
    "dynamodb": {
        "L-F98FE922": {"method": "list_tables", "key": "TableNames", "fields": [],},
        "global": False,
    },
    "ebs": {
        "L-309BACF6": {
            "method": "describe_snapshots",
            "key": "Snapshots",
            "fields": [],
            "filter": {"OwnerIds": ["self"]},
        },
        "L-D18FCD1D": {
            "method": "describe_volumes",
            "key": "Volumes",
            "fields": "Size",
            "divisor": 1000,
            "filter": {"Filters": [{"Name": "volume-type", "Values": ["gp2",],}]},
        },
        "L-9CF3C2EB": {
            "method": "describe_volumes",
            "key": "Volumes",
            "fields": "Size",
            "divisor": 1000,
            "filter": {"Filters": [{"Name": "volume-type", "Values": ["standard",],}]},
        },
        "L-FD252861": {
            "method": "describe_volumes",
            "key": "Volumes",
            "fields": "Size",
            "divisor": 1000,
            "filter": {"Filters": [{"Name": "volume-type", "Values": ["io1",],}]},
        },
        "L-17AF77E8": {
            "method": "describe_volumes",
            "key": "Volumes",
            "fields": "Size",
            "divisor": 1000,
            "filter": {"Filters": [{"Name": "volume-type", "Values": ["sc1",],}]},
        },
        "L-82ACEF56": {
            "method": "describe_volumes",
            "key": "Volumes",
            "fields": "Size",
            "divisor": 1000,
            "filter": {"Filters": [{"Name": "volume-type", "Values": ["st1",],}]},
        },
        "L-B3A130E6": {
            "method": "describe_volumes",
            "key": "Volumes",
            "fields": "Iops",
            "filter": {"Filters": [{"Name": "volume-type", "Values": ["io1",],}]},
        },
        "global": False,
    },
    "ec2": {
        "L-0263D0A3": {
            "method": "describe_addresses",
            "key": "Addresses",
            "fields": [],
        },
        "L-74FC7D96": {
            "method": "describe_instances",
            "key": "Reservations",
            "fields": [],
            "filter": {
                "Filters": [
                    {
                        "Name": "instance-type",
                        "Values": ["f1.2xlarge", "f1.4xlarge", "f1.16xlarge"],
                    }
                ]
            },
        },
        "L-DB2E81BA": {
            "method": "describe_instances",
            "key": "Reservations",
            "fields": [],
            "filter": {
                "Filters": [
                    {
                        "Name": "instance-type",
                        "Values": [
                            "g3s.xlarge",
                            "g3.4xlarge",
                            "g3.8xlarge",
                            "g3.16xlarge",
                            "g4dn.xlarge",
                            "g4dn.2xlarge",
                            "g4dn.4xlarge",
                            "g4dn.8xlarge",
                            "g4dn.16xlarge",
                            "g4dn.12xlarge",
                            "g4dn.metal",
                        ],
                    }
                ]
            },
        },
        "L-1945791B": {
            "method": "describe_instances",
            "key": "Reservations",
            "fields": [],
            "filter": {
                "Filters": [
                    {
                        "Name": "instance-type",
                        "Values": [
                            "inf1.xlarge",
                            "inf1.2xlarge",
                            "inf1.6xlarge",
                            "inf1.24xlarge",
                        ],
                    }
                ]
            },
        },
        "L-417A185B": {
            "method": "describe_instances",
            "key": "Reservations",
            "fields": [],
            "filter": {
                "Filters": [
                    {
                        "Name": "instance-type",
                        "Values": [
                            "p2.xlarge",
                            "p2.8xlarge",
                            "p2.16xlarge",
                            "p3.2xlarge",
                            "p3.8xlarge",
                            "p3.16xlarge",
                            "p3dn.24xlarge",
                        ],
                    }
                ]
            },
        },
        "L-1216C47A": {
            "method": "describe_instances",
            "key": "Reservations",
            "fields": [],
            "filter": {
                "Filters": [
                    {
                        "Name": "instance-type",
                        "Values": [
                            "c5d.large",
                            "c5d.xlarge",
                            "c5d.2xlarge",
                            "c5d.4xlarge",
                            "c5d.9xlarge",
                            "c5d.12xlarge",
                            "c5d.18xlarge",
                            "c5d.24xlarge",
                            "c5d.metal",
                            "c5a.large",
                            "c5a.xlarge",
                            "c5a.2xlarge",
                            "c5a.4xlarge",
                            "c5a.8xlarge",
                            "c5a.12xlarge",
                            "c5a.16xlarge",
                            "c5a.24xlarge",
                            "c5n.large",
                            "c5n.xlarge",
                            "c5n.2xlarge",
                            "c5n.4xlarge",
                            "c5n.9xlarge",
                            "c5n.18xlarge",
                            "c5n.metal",
                            "c4.large",
                            "c4.xlarge",
                            "c4.2xlarge",
                            "c4.4xlarge",
                            "c4.8xlarge",
                            "d2.xlarge",
                            "d2.2xlarge",
                            "d2.4xlarge",
                            "d2.8xlarge",
                            "h1.2xlarge",
                            "h1.4xlarge",
                            "h1.8xlarge",
                            "h1.16xlarge",
                            "i3.large",
                            "i3.xlarge",
                            "i3.2xlarge",
                            "i3.4xlarge",
                            "i3.8xlarge",
                            "i3.16xlarge",
                            "i3.metal",
                            "m6g.medium",
                            "m6g.large",
                            "m6g.xlarge",
                            "m6g.2xlarge",
                            "m6g.4xlarge",
                            "m6g.8xlarge",
                            "m6g.12xlarge",
                            "m6g.16xlarge",
                            "m6g.metal",
                            "m5.large",
                            "m5.xlarge",
                            "m5.2xlarge",
                            "m5.4xlarge",
                            "m5.8xlarge",
                            "m5.12xlarge",
                            "m5.16xlarge",
                            "m5.24xlarge",
                            "m5.metal",
                            "m5d.large",
                            "m5d.xlarge",
                            "m5d.2xlarge",
                            "m5d.4xlarge",
                            "m5d.8xlarge",
                            "m5d.12xlarge",
                            "m5d.16xlarge",
                            "m5d.24xlarge",
                            "m5d.metal",
                            "m5a.large",
                            "m5a.xlarge",
                            "m5a.2xlarge",
                            "m5a.4xlarge",
                            "m5a.8xlarge",
                            "m5a.12xlarge",
                            "m5a.16xlarge",
                            "m5a.24xlarge",
                            "m5ad.large",
                            "m5ad.xlarge",
                            "m5ad.2xlarge",
                            "m5ad.4xlarge",
                            "m5ad.12xlarge",
                            "m5ad.24xlarge",
                            "m5n.large",
                            "m5n.xlarge",
                            "m5n.2xlarge",
                            "m5n.4xlarge",
                            "m5n.8xlarge",
                            "m5n.12xlarge",
                            "m5n.16xlarge",
                            "m5n.24xlarge",
                            "m5dn.large",
                            "m5dn.xlarge",
                            "m5dn.2xlarge",
                            "m5dn.4xlarge",
                            "m5dn.8xlarge",
                            "m5dn.12xlarge",
                            "m5dn.16xlarge",
                            "m5dn.24xlarge",
                            "m4.large",
                            "m4.xlarge",
                            "m4.2xlarge",
                            "m4.4xlarge",
                            "m4.10xlarge",
                            "m4.16xlarge",
                            "z1d.large",
                            "z1d.xlarge",
                            "z1d.2xlarge",
                            "z1d.3xlarge",
                            "z1d.6xlarge",
                            "z1d.12xlarge",
                            "z1d.metal",
                            "r6g.medium",
                            "r6g.large",
                            "r6g.xlarge",
                            "r6g.2xlarge",
                            "r6g.4xlarge",
                            "r6g.8xlarge",
                            "r6g.12xlarge",
                            "r6g.16xlarge",
                            "r6g.metal",
                            "r5.large",
                            "r5.xlarge",
                            "r5.2xlarge",
                            "r5.4xlarge",
                            "r5.8xlarge",
                            "r5.12xlarge",
                            "r5.16xlarge",
                            "r5.24xlarge",
                            "r5.metal",
                            "r5d.large",
                            "r5d.xlarge",
                            "r5d.2xlarge",
                            "r5d.4xlarge",
                            "r5d.8xlarge",
                            "r5d.12xlarge",
                            "r5d.16xlarge",
                            "r5d.24xlarge",
                            "r5d.metal",
                            "r5a.large",
                            "r5a.xlarge",
                            "r5a.2xlarge",
                            "r5a.4xlarge",
                            "r5a.8xlarge",
                            "r5a.12xlarge",
                            "r5a.16xlarge",
                            "r5a.24xlarge",
                            "r5ad.large",
                            "r5ad.xlarge",
                            "r5ad.2xlarge",
                            "r5ad.4xlarge",
                            "r5ad.12xlarge",
                            "r5ad.24xlarge",
                            "r5n.large",
                            "r5n.xlarge",
                            "r5n.2xlarge",
                            "r5n.4xlarge",
                            "r5n.8xlarge",
                            "r5n.12xlarge",
                            "r5n.16xlarge",
                            "r5n.24xlarge",
                            "r5dn.large",
                            "r5dn.xlarge",
                            "r5dn.2xlarge",
                            "r5dn.4xlarge",
                            "r5dn.8xlarge",
                            "r5dn.12xlarge",
                            "r5dn.16xlarge",
                            "r5dn.24xlarge",
                            "r4.large",
                            "r4.xlarge",
                            "r4.2xlarge",
                            "r4.4xlarge",
                            "r4.8xlarge",
                            "r4.16xlarge",
                            "t3.nano",
                            "t3.micro",
                            "t3.small",
                            "t3.medium",
                            "t3.large",
                            "t3.xlarge",
                            "t3.2xlarge",
                            "t3a.nano",
                            "t3a.micro",
                            "t3a.small",
                            "t3a.medium",
                            "t3a.large",
                            "t3a.xlarge",
                            "t3a.2xlarge",
                            "t2.nano",
                            "t2.micro",
                            "t2.small",
                            "t2.medium",
                            "t2.large",
                            "t2.xlarge",
                            "t2.2xlarge",
                        ],
                    }
                ]
            },
        },
        "L-7295265B": {
            "method": "describe_instances",
            "key": "Reservations",
            "fields": [],
            "filter": {
                "Filters": [
                    {
                        "Name": "instance-type",
                        "Values": [
                            "x1e.xlarge",
                            "x1e.2xlarge",
                            "x1e.4xlarge",
                            "x1e.8xlarge",
                            "x1e.16xlarge",
                            "x1e.32xlarge",
                            "x1.16xlarge",
                            "x1.32xlarge",
                        ],
                    }
                ]
            },
        },
        "L-949445B0": {
            "method": "describe_hosts",
            "key": "Hosts",
            "fields": [],
            "filter": {"Filters": [{"Name": "instance-type", "Values": ["a1",],}]},
        },
        "L-8D142A2E": {
            "method": "describe_hosts",
            "key": "Hosts",
            "fields": [],
            "filter": {"Filters": [{"Name": "instance-type", "Values": ["c3",],}]},
        },
        "L-E4BF28E0": {
            "method": "describe_hosts",
            "key": "Hosts",
            "fields": [],
            "filter": {"Filters": [{"Name": "instance-type", "Values": ["c4",],}]},
        },
        "L-81657574": {
            "method": "describe_hosts",
            "key": "Hosts",
            "fields": [],
            "filter": {"Filters": [{"Name": "instance-type", "Values": ["c5",],}]},
        },
        "L-C93F66A2": {
            "method": "describe_hosts",
            "key": "Hosts",
            "fields": [],
            "filter": {"Filters": [{"Name": "instance-type", "Values": ["c5d",],}]},
        },
        "L-20F13EBD": {
            "method": "describe_hosts",
            "key": "Hosts",
            "fields": [],
            "filter": {"Filters": [{"Name": "instance-type", "Values": ["C5n",],}]},
        },
        "L-A749B537": {
            "method": "describe_hosts",
            "key": "Hosts",
            "fields": [],
            "filter": {"Filters": [{"Name": "instance-type", "Values": ["c6g",],}]},
        },
        "L-8B27377A": {
            "method": "describe_hosts",
            "key": "Hosts",
            "fields": [],
            "filter": {"Filters": [{"Name": "instance-type", "Values": ["d2",],}]},
        },
        "L-5C4CD236": {
            "method": "describe_hosts",
            "key": "Hosts",
            "fields": [],
            "filter": {"Filters": [{"Name": "instance-type", "Values": ["f1",],}]},
        },
        "L-74BBB7CB": {
            "method": "describe_hosts",
            "key": "Hosts",
            "fields": [],
            "filter": {"Filters": [{"Name": "instance-type", "Values": ["g2",],}]},
        },
        "L-DE82EABA": {
            "method": "describe_hosts",
            "key": "Hosts",
            "fields": [],
            "filter": {"Filters": [{"Name": "instance-type", "Values": ["g3",],}]},
        },
        "L-9675FDCD": {
            "method": "describe_hosts",
            "key": "Hosts",
            "fields": [],
            "filter": {"Filters": [{"Name": "instance-type", "Values": ["g3s",],}]},
        },
        "L-CAE24619": {
            "method": "describe_hosts",
            "key": "Hosts",
            "fields": [],
            "filter": {"Filters": [{"Name": "instance-type", "Values": ["g4dn",],}]},
        },
        "L-84391ECC": {
            "method": "describe_hosts",
            "key": "Hosts",
            "fields": [],
            "filter": {"Filters": [{"Name": "instance-type", "Values": ["h1",],}]},
        },
        "L-6222C1B6": {
            "method": "describe_hosts",
            "key": "Hosts",
            "fields": [],
            "filter": {"Filters": [{"Name": "instance-type", "Values": ["i2",],}]},
        },
        "L-8E60B0B1": {
            "method": "describe_hosts",
            "key": "Hosts",
            "fields": [],
            "filter": {"Filters": [{"Name": "instance-type", "Values": ["i3",],}]},
        },
        "L-77EE2B11": {
            "method": "describe_hosts",
            "key": "Hosts",
            "fields": [],
            "filter": {"Filters": [{"Name": "instance-type", "Values": ["i3en",],}]},
        },
        "L-5480EFD2": {
            "method": "describe_hosts",
            "key": "Hosts",
            "fields": [],
            "filter": {"Filters": [{"Name": "instance-type", "Values": ["inf1",],}]},
        },
        "L-3C82F907": {
            "method": "describe_hosts",
            "key": "Hosts",
            "fields": [],
            "filter": {"Filters": [{"Name": "instance-type", "Values": ["m3",],}]},
        },
        "L-EF30B25E": {
            "method": "describe_hosts",
            "key": "Hosts",
            "fields": [],
            "filter": {"Filters": [{"Name": "instance-type", "Values": ["m4",],}]},
        },
        "L-8B7BF662": {
            "method": "describe_hosts",
            "key": "Hosts",
            "fields": [],
            "filter": {"Filters": [{"Name": "instance-type", "Values": ["m5",],}]},
        },
        "L-B10F70D6": {
            "method": "describe_hosts",
            "key": "Hosts",
            "fields": [],
            "filter": {"Filters": [{"Name": "instance-type", "Values": ["M5a",],}]},
        },
        "L-74F41837": {
            "method": "describe_hosts",
            "key": "Hosts",
            "fields": [],
            "filter": {"Filters": [{"Name": "instance-type", "Values": ["M5ad",],}]},
        },
        "L-8CCBD91B": {
            "method": "describe_hosts",
            "key": "Hosts",
            "fields": [],
            "filter": {"Filters": [{"Name": "instance-type", "Values": ["m5d",],}]},
        },
        "L-DA07429F": {
            "method": "describe_hosts",
            "key": "Hosts",
            "fields": [],
            "filter": {"Filters": [{"Name": "instance-type", "Values": ["m5dn",],}]},
        },
        "L-24D7D4AD": {
            "method": "describe_hosts",
            "key": "Hosts",
            "fields": [],
            "filter": {"Filters": [{"Name": "instance-type", "Values": ["m5n",],}]},
        },
        "L-D50A37FA": {
            "method": "describe_hosts",
            "key": "Hosts",
            "fields": [],
            "filter": {"Filters": [{"Name": "instance-type", "Values": ["m6g",],}]},
        },
        "L-2753CF59": {
            "method": "describe_hosts",
            "key": "Hosts",
            "fields": [],
            "filter": {"Filters": [{"Name": "instance-type", "Values": ["p2",],}]},
        },
        "L-A0A19F79": {
            "method": "describe_hosts",
            "key": "Hosts",
            "fields": [],
            "filter": {"Filters": [{"Name": "instance-type", "Values": ["p3",],}]},
        },
        "L-B601B3B6": {
            "method": "describe_hosts",
            "key": "Hosts",
            "fields": [],
            "filter": {"Filters": [{"Name": "instance-type", "Values": ["p3dn",],}]},
        },
        "L-B7208018": {
            "method": "describe_hosts",
            "key": "Hosts",
            "fields": [],
            "filter": {"Filters": [{"Name": "instance-type", "Values": ["r3",],}]},
        },
        "L-313524BA": {
            "method": "describe_hosts",
            "key": "Hosts",
            "fields": [],
            "filter": {"Filters": [{"Name": "instance-type", "Values": ["r4",],}]},
        },
        "L-EA4FD6CF": {
            "method": "describe_hosts",
            "key": "Hosts",
            "fields": [],
            "filter": {"Filters": [{"Name": "instance-type", "Values": ["r5",],}]},
        },
        "L-8FE30D52": {
            "method": "describe_hosts",
            "key": "Hosts",
            "fields": [],
            "filter": {"Filters": [{"Name": "instance-type", "Values": ["R5a",],}]},
        },
        "L-EC7178B6": {
            "method": "describe_hosts",
            "key": "Hosts",
            "fields": [],
            "filter": {"Filters": [{"Name": "instance-type", "Values": ["R5ad",],}]},
        },
        "L-8814B54F": {
            "method": "describe_hosts",
            "key": "Hosts",
            "fields": [],
            "filter": {"Filters": [{"Name": "instance-type", "Values": ["r5d",],}]},
        },
        "L-4AB14223": {
            "method": "describe_hosts",
            "key": "Hosts",
            "fields": [],
            "filter": {"Filters": [{"Name": "instance-type", "Values": ["r5dn",],}]},
        },
        "L-52EF324A": {
            "method": "describe_hosts",
            "key": "Hosts",
            "fields": [],
            "filter": {"Filters": [{"Name": "instance-type", "Values": ["r5n",],}]},
        },
        "L-B6D6065D": {
            "method": "describe_hosts",
            "key": "Hosts",
            "fields": [],
            "filter": {"Filters": [{"Name": "instance-type", "Values": ["r6g",],}]},
        },
        "L-DE3D9563": {
            "method": "describe_hosts",
            "key": "Hosts",
            "fields": [],
            "filter": {"Filters": [{"Name": "instance-type", "Values": ["x1",],}]},
        },
        "L-DEF8E115": {
            "method": "describe_hosts",
            "key": "Hosts",
            "fields": [],
            "filter": {"Filters": [{"Name": "instance-type", "Values": ["x1e",],}]},
        },
        "L-F035E935": {
            "method": "describe_hosts",
            "key": "Hosts",
            "fields": [],
            "filter": {"Filters": [{"Name": "instance-type", "Values": ["z1d",],}]},
        },
        "global": False,
    },
    "ecr": {
        "L-CFEB8E8D": {
            "method": "describe_repositories",
            "key": "repositories",
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
        "L-D64F1F14": {
            "method": "describe_application_versions",
            "key": "ApplicationVersions",
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
    "elastic-inference": {
        "L-495D9A1B": {
            "method": "describe_accelerators",
            "key": "acceleratorSet",
            "fields": [],
        },
        "global": False,
    },
    "es": {
        "L-076D529E": {
            "method": "list_domain_names",
            "key": "DomainNames",
            "fields": [],
        },
        "global": False,
    },
    "forecast": {
        "L-D87814A4": {"method": "list_predictors", "key": "Predictors", "fields": [],},
        "L-B3A7DE22": {
            "method": "list_dataset_import_jobs",
            "key": "DatasetImportJobs",
            "fields": [],
        },
        "L-A8E1A12A": {"method": "get_outcomes", "key": "outcomes", "fields": [],},
        "global": False,
    },
    "frauddetector": {
        "L-EB925C6F": {"method": "get_detectors", "key": "detectors", "fields": [],},
        "L-A499790A": {"method": "get_models", "key": "models", "fields": [],},
        "L-A8E1A12A": {"method": "get_outcomes", "key": "outcomes", "fields": [],},
        "global": False,
    },
    "gamelift": {
        "L-AED4A06A": {"method": "list_aliases", "key": "Aliases", "fields": [],},
        "L-90D24F1B": {"method": "list_builds", "key": "Builds", "fields": [],},
        "L-FDDD1260": {"method": "list_fleets", "key": "FleetIds", "fields": [],},
        "L-8D885299": {
            "method": "list_game_server_groups",
            "key": "GameServerGroups",
            "fields": [],
        },
        "global": False,
    },
    "glue": {
        "L-F953935E": {"method": "get_databases", "key": "DatabaseList", "fields": [],},
        "L-D987EC31": {
            "method": "get_user_defined_functions",
            "key": "UserDefinedFunctions",
            "fields": [],
            "filter": {"Pattern": "*"},
        },
        "L-83192DBF": {
            "method": "get_security_configurations",
            "key": "SecurityConfigurations",
            "fields": [],
        },
        "L-F1653A6D": {"method": "get_triggers", "key": "Triggers", "fields": [],},
        "L-11FA2C1A": {"method": "get_crawlers", "key": "Crawlers", "fields": [],},
        "L-7DD7C33A": {"method": "list_workflows", "key": "Workflows", "fields": [],},
        "L-04CEE988": {
            "method": "list_ml_transforms",
            "key": "TransformIds",
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
    "inspector": {
        "L-E1AFB5F4": {
            "method": "list_assessment_targets",
            "key": "assessmentTargetArns",
            "fields": [],
        },
        "L-7A3AEC10": {
            "method": "list_assessment_templates",
            "key": "assessmentTemplateArns",
            "fields": [],
        },
        "L-12943E2F": {
            "method": "list_assessment_runs",
            "key": "assessmentRunArns",
            "fields": [],
        },
        "global": False,
    },
    "kendra": {
        "L-51C776DF": {
            "method": "list_indices",
            "key": "IndexConfigurationSummaryItems",
            "fields": [],
        },
        "global": False,
    },
    "kms": {
        "L-C2F1777E": {"method": "list_keys", "key": "Keys", "fields": [],},
        "L-2601EE20": {"method": "list_aliases", "key": "Aliases", "fields": [],},
        "global": False,
    },
    "logs": {
        "L-D2832119": {
            "method": "describe_log_groups",
            "key": "logGroups",
            "fields": [],
        },
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
    "networkmanager": {
        "L-2418390E": {
            "method": "describe_global_networks",
            "key": "GlobalNetworks",
            "fields": [],
        },
        "global": True,
    },
    "polly": {
        "L-BC40090A": {"method": "list_lexicons", "key": "Lexicons", "fields": [],},
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
        "L-7ADDB58A": {
            "method": "describe_db_instances",
            "key": "DBInstances",
            "fields": "AllocatedStorage",
        },
        "L-D94C7EA3": {
            "method": "describe_db_proxies",
            "key": "DBProxies",
            "fields": [],
        },
        "L-732153D0": {
            "method": "describe_db_security_groups",
            "key": "DBSecurityGroups",
            "fields": [],
        },
        "L-48C6BF61": {
            "method": "describe_db_subnet_groups",
            "key": "DBSubnetGroups",
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
    "swf": {
        "L-464CCB53": {
            "method": "list_domains",
            "key": "domainInfos",
            "fields": [],
            "filter": {"registrationStatus": "REGISTERED"},
        },
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

# These resources are not covered by services-quota, than we must use "manual" checks
SPECIAL_RESOURCES = ["ses"]

FILTER_EC2_BIGFAMILY = {
    "filter": {
        "Filters": [
            {
                "Name": "instance-type",
                "Values": [
                    "a1.medium",
                    "a1.large",
                    "a1.xlarge",
                    "a1.2xlarge",
                    "a1.4xlarge",
                    "a1.metal",
                    "c6g.medium",
                    "c6g.large",
                    "c6g.xlarge",
                    "c6g.2xlarge",
                    "c6g.4xlarge",
                    "c6g.8xlarge",
                    "c6g.12xlarge",
                    "c6g.16xlarge",
                    "c6g.metal",
                    "c5.large",
                    "c5.xlarge",
                    "c5.2xlarge",
                    "c5.4xlarge",
                    "c5.9xlarge",
                    "c5.12xlarge",
                    "c5.18xlarge",
                    "c5.24xlarge",
                    "c5.metal",
                ],
            }
        ]
    },
}
