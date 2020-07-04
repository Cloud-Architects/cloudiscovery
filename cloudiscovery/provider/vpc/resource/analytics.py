import json
from typing import List

from provider.vpc.command import VpcOptions, check_ipvpc_inpolicy
from provider.vpc.resource.database import RDS
from shared.common import (
    datetime_to_string,
    ResourceProvider,
    Resource,
    message_handler,
    ResourceDigest,
    ResourceEdge,
    ResourceAvailable,
)
from shared.common_aws import resource_tags
from shared.error_handler import exception


class ELASTICSEARCH(ResourceProvider):
    def __init__(self, vpc_options: VpcOptions):
        """
        Elasticsearch

        :param vpc_options:
        """
        super().__init__()
        self.vpc_options = vpc_options

    @exception
    @ResourceAvailable(services="es")
    def get_resources(self) -> List[Resource]:

        client = self.vpc_options.client("es")

        resources_found = []

        response = client.list_domain_names()

        if self.vpc_options.verbose:
            message_handler("Collecting data from Elasticsearch Domains...", "HEADER")

        for data in response["DomainNames"]:

            elasticsearch_domain = client.describe_elasticsearch_domain(
                DomainName=data["DomainName"]
            )

            documentpolicy = elasticsearch_domain["DomainStatus"]["AccessPolicies"]

            document = json.dumps(documentpolicy, default=datetime_to_string)

            # check either vpc_id or potencial subnet ip are found
            ipvpc_found = check_ipvpc_inpolicy(
                document=document, vpc_options=self.vpc_options
            )

            # elasticsearch uses accesspolicies too, so check both situation
            if (
                elasticsearch_domain["DomainStatus"]["VPCOptions"]["VPCId"]
                == self.vpc_options.vpc_id
                or ipvpc_found is True
            ):
                list_tags_response = client.list_tags(
                    ARN=elasticsearch_domain["DomainStatus"]["ARN"]
                )
                digest = ResourceDigest(
                    id=elasticsearch_domain["DomainStatus"]["DomainId"],
                    type="aws_elasticsearch_domain",
                )
                resources_found.append(
                    Resource(
                        digest=digest,
                        name=elasticsearch_domain["DomainStatus"]["DomainName"],
                        details="",
                        group="analytics",
                        tags=resource_tags(list_tags_response),
                    )
                )
                for subnet_id in elasticsearch_domain["DomainStatus"]["VPCOptions"][
                    "SubnetIds"
                ]:
                    self.relations_found.append(
                        ResourceEdge(
                            from_node=digest,
                            to_node=ResourceDigest(id=subnet_id, type="aws_subnet"),
                        )
                    )
        return resources_found


class MSK(ResourceProvider):
    def __init__(self, vpc_options: VpcOptions):
        """
        Msk

        :param vpc_options:
        """
        super().__init__()
        self.vpc_options = vpc_options

    @exception
    @ResourceAvailable(services="kafka")
    def get_resources(self) -> List[Resource]:

        client = self.vpc_options.client("kafka")

        resources_found = []

        # get all cache clusters
        response = client.list_clusters()

        if self.vpc_options.verbose:
            message_handler("Collecting data from MSK Clusters...", "HEADER")

        # iterate cache clusters to get subnet groups
        for data in response["ClusterInfoList"]:

            msk_subnets = ", ".join(data["BrokerNodeGroupInfo"]["ClientSubnets"])

            ec2 = self.vpc_options.session.resource(
                "ec2", region_name=self.vpc_options.region_name
            )

            filters = [{"Name": "vpc-id", "Values": [self.vpc_options.vpc_id]}]

            subnets = ec2.subnets.filter(Filters=filters)

            for subnet in list(subnets):

                if subnet.id in msk_subnets:
                    digest = ResourceDigest(
                        id=data["ClusterArn"], type="aws_msk_cluster"
                    )
                    resources_found.append(
                        Resource(
                            digest=digest,
                            name=data["ClusterName"],
                            details="",
                            group="analytics",
                            tags=resource_tags(data),
                        )
                    )
                    self.relations_found.append(
                        ResourceEdge(
                            from_node=digest,
                            to_node=ResourceDigest(id=subnet.id, type="aws_subnet"),
                        )
                    )

                    break
        return resources_found


class QUICKSIGHT(ResourceProvider):
    def __init__(self, vpc_options: VpcOptions):
        """
        Quicksight

        :param vpc_options:
        """
        super().__init__()
        self.vpc_options = vpc_options

    @exception
    @ResourceAvailable(services="quicksight")
    def get_resources(self) -> List[Resource]:

        client = self.vpc_options.client("quicksight")

        resources_found = []

        # Get accountid
        account_id = self.vpc_options.account_number()

        response = client.list_data_sources(AwsAccountId=account_id)

        if self.vpc_options.verbose:
            message_handler("Collecting data from Quicksight...", "HEADER")

        for data in response["DataSources"]:

            # Twitter and S3 data source is not supported
            if data["Type"] not in ("TWITTER", "S3", "ATHENA"):

                data_source = client.describe_data_source(
                    AwsAccountId=account_id, DataSourceId=data["DataSourceId"]
                )

                if "RdsParameters" in data_source["DataSource"]["DataSourceParameters"]:

                    instance_id = data_source["DataSource"]["DataSourceParameters"][
                        "RdsParameters"
                    ]["InstanceId"]
                    rds = RDS(self.vpc_options).get_resources(instance_id=instance_id)

                    if rds:

                        quicksight_digest = ResourceDigest(
                            id=data["DataSourceId"], type="aws_quicksight"
                        )
                        resources_found.append(
                            Resource(
                                digest=quicksight_digest,
                                name=data["Name"],
                                details="",
                                group="analytics",
                                tags=resource_tags(data),
                            )
                        )

                        self.relations_found.append(
                            ResourceEdge(
                                from_node=quicksight_digest, to_node=rds[0].digest,
                            )
                        )

                if "VpcConnectionProperties" in data_source:

                    if (
                        self.vpc_options.vpc_id
                        in data_source["VpcConnectionProperties"]["VpcConnectionArn"]
                    ):
                        quicksight_digest = ResourceDigest(
                            id=data["DataSourceId"], type="aws_quicksight"
                        )
                        resources_found.append(
                            Resource(
                                digest=quicksight_digest,
                                name=data["DataSourceId"],
                                details="",
                                group="analytics",
                                tags=resource_tags(data),
                            )
                        )

                        self.relations_found.append(
                            ResourceEdge(
                                from_node=quicksight_digest,
                                to_node=ResourceDigest(
                                    id=self.vpc_options.vpc_id, type="aws_vpc"
                                ),
                            )
                        )

        return resources_found
