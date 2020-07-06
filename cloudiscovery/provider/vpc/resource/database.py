from typing import List

from provider.vpc.command import VpcOptions
from shared.common import (
    ResourceProvider,
    Resource,
    message_handler,
    ResourceDigest,
    ResourceEdge,
    ResourceAvailable,
)
from shared.common_aws import resource_tags
from shared.error_handler import exception


class RDS(ResourceProvider):
    def __init__(self, vpc_options: VpcOptions):
        """
        RDS

        :param vpc_options:
        """
        super().__init__()
        self.vpc_options = vpc_options

    @exception
    @ResourceAvailable(services="rds")
    def get_resources(self, instance_id=None) -> List[Resource]:

        client = self.vpc_options.client("rds")

        params = {
            "Name": "engine",
            "Values": [
                "aurora",
                "aurora-mysql",
                "aurora-postgresql",
                "mariadb",
                "mysql",
                "oracle-ee",
                "oracle-se2",
                "oracle-se1",
                "oracle-se",
                "postgres",
                "sqlserver-ee",
                "sqlserver-se",
                "sqlserver-ex",
                "sqlserver-web",
            ],
        }

        if instance_id is not None:
            params.update({"Name": "db-instance-id", "Values": [instance_id]})

        resources_found = []

        response = client.describe_db_instances(Filters=[params])

        if instance_id is None and self.vpc_options.verbose:
            message_handler("Collecting data from RDS Instances...", "HEADER")

        for data in response["DBInstances"]:
            if data["DBSubnetGroup"]["VpcId"] == self.vpc_options.vpc_id:
                tags_response = client.list_tags_for_resource(
                    ResourceName=data["DBInstanceArn"]
                )

                rds_digest = ResourceDigest(
                    id=data["DBInstanceArn"], type="aws_db_instance"
                )
                subnet_ids = []
                for subnet in data["DBSubnetGroup"]["Subnets"]:
                    subnet_ids.append(subnet["SubnetIdentifier"])
                    self.relations_found.append(
                        ResourceEdge(
                            from_node=rds_digest,
                            to_node=ResourceDigest(
                                id=subnet["SubnetIdentifier"], type="aws_subnet"
                            ),
                        )
                    )

                resources_found.append(
                    Resource(
                        digest=rds_digest,
                        name=data["DBInstanceIdentifier"],
                        details="DBInstance using subnets {} and engine {}".format(
                            ", ".join(subnet_ids), data["Engine"]
                        ),
                        group="database",
                        tags=resource_tags(tags_response),
                    )
                )

        return resources_found


class ELASTICACHE(ResourceProvider):
    def __init__(self, vpc_options: VpcOptions):
        """
        Elasticache

        :param vpc_options:
        """
        super().__init__()
        self.vpc_options = vpc_options

    @exception
    @ResourceAvailable(services="elasticache")
    def get_resources(self) -> List[Resource]:

        client = self.vpc_options.client("elasticache")

        resources_found = []

        # get all cache clusters
        response = client.describe_cache_clusters()

        if self.vpc_options.verbose:
            message_handler("Collecting data from Elasticache Clusters...", "HEADER")

        # iterate cache clusters to get subnet groups
        for data in response["CacheClusters"]:

            cachesubnet = client.describe_cache_subnet_groups(
                CacheSubnetGroupName=data["CacheSubnetGroupName"]
            )

            if cachesubnet["CacheSubnetGroups"][0]["VpcId"] == self.vpc_options.vpc_id:
                ec_digest = ResourceDigest(
                    id=data["CacheClusterId"], type="aws_elasticache_cluster"
                )
                subnet_ids = []
                for subnet in cachesubnet["CacheSubnetGroups"][0]["Subnets"]:
                    subnet_ids.append(subnet["SubnetIdentifier"])
                    self.relations_found.append(
                        ResourceEdge(
                            from_node=ec_digest,
                            to_node=ResourceDigest(
                                id=subnet["SubnetIdentifier"], type="aws_subnet"
                            ),
                        )
                    )

                resources_found.append(
                    Resource(
                        digest=ec_digest,
                        name=data["CacheSubnetGroupName"],
                        details="Elasticache Cluster using subnets {} and engine {}".format(
                            ", ".join(subnet_ids), data["Engine"]
                        ),
                        group="database",
                    )
                )

        return resources_found


class DOCUMENTDB(ResourceProvider):
    def __init__(self, vpc_options: VpcOptions):
        """
        Documentdb

        :param vpc_options:
        """
        super().__init__()
        self.vpc_options = vpc_options

    @exception
    @ResourceAvailable(services="docdb")
    def get_resources(self) -> List[Resource]:

        client = self.vpc_options.client("docdb")

        resources_found = []

        response = client.describe_db_instances(
            Filters=[{"Name": "engine", "Values": ["docdb"]}]
        )

        if self.vpc_options.verbose:
            message_handler("Collecting data from DocumentDB Instances...", "HEADER")

        # iterate cache clusters to get subnet groups
        for data in response["DBInstances"]:

            if data["DBSubnetGroup"]["VpcId"] == self.vpc_options.vpc_id:
                tags_response = client.list_tags_for_resource(
                    ResourceName=data["DBInstanceArn"]
                )
                docdb_digest = ResourceDigest(
                    id=data["DBInstanceArn"], type="aws_docdb_cluster"
                )
                subnet_ids = []
                for subnet in data["DBSubnetGroup"]["Subnets"]:
                    subnet_ids.append(subnet["SubnetIdentifier"])
                    self.relations_found.append(
                        ResourceEdge(
                            from_node=docdb_digest,
                            to_node=ResourceDigest(
                                id=subnet["SubnetIdentifier"], type="aws_subnet"
                            ),
                        )
                    )
                resources_found.append(
                    Resource(
                        digest=docdb_digest,
                        name=data["DBInstanceIdentifier"],
                        details="Documentdb using subnets {} and engine {}".format(
                            ", ".join(subnet_ids), data["Engine"]
                        ),
                        group="database",
                        tags=resource_tags(tags_response),
                    )
                )

        return resources_found


class NEPTUNE(ResourceProvider):
    def __init__(self, vpc_options: VpcOptions):
        """
        Neptune

        :param vpc_options:
        """
        super().__init__()
        self.vpc_options = vpc_options

    @exception
    @ResourceAvailable(services="neptune")
    def get_resources(self) -> List[Resource]:

        client = self.vpc_options.client("neptune")

        resources_found = []

        response = client.describe_db_instances(
            Filters=[{"Name": "engine", "Values": ["neptune"]}]
        )

        if self.vpc_options.verbose:
            message_handler("Collecting data from Neptune Instances...", "HEADER")

        # iterate cache clusters to get subnet groups
        for data in response["DBInstances"]:

            if data["DBSubnetGroup"]["VpcId"] == self.vpc_options.vpc_id:
                tags_response = client.list_tags_for_resource(
                    ResourceName=data["DBInstanceArn"]
                )
                neptune_digest = ResourceDigest(
                    id=data["DBInstanceArn"], type="aws_neptune_cluster"
                )
                subnet_ids = []
                for subnet in data["DBSubnetGroup"]["Subnets"]:
                    subnet_ids.append(subnet["SubnetIdentifier"])
                    self.relations_found.append(
                        ResourceEdge(
                            from_node=neptune_digest,
                            to_node=ResourceDigest(
                                id=subnet["SubnetIdentifier"], type="aws_subnet"
                            ),
                        )
                    )
                resources_found.append(
                    Resource(
                        digest=neptune_digest,
                        name=data["DBInstanceIdentifier"],
                        details="Neptune using subnets {} and engine {}".format(
                            ", ".join(subnet_ids), data["Engine"]
                        ),
                        group="database",
                        tags=resource_tags(tags_response),
                    )
                )

        return resources_found
