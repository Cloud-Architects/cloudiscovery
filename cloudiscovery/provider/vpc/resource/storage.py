import json
from concurrent.futures.thread import ThreadPoolExecutor
from typing import List

from botocore.exceptions import ClientError

from provider.vpc.command import VpcOptions, check_ipvpc_inpolicy
from shared.common import (
    ResourceProvider,
    Resource,
    message_handler,
    ResourceDigest,
    ResourceEdge,
    datetime_to_string,
    ResourceAvailable,
)
from shared.common_aws import describe_subnet, resource_tags, get_name_tag
from shared.error_handler import exception


class EFS(ResourceProvider):
    def __init__(self, vpc_options: VpcOptions):
        """
        Efs

        :param vpc_options:
        """
        super().__init__()
        self.vpc_options = vpc_options

    @exception
    @ResourceAvailable(services="efs")
    def get_resources(self) -> List[Resource]:

        client = self.vpc_options.client("efs")

        resources_found = []

        # get filesystems available
        response = client.describe_file_systems()

        if self.vpc_options.verbose:
            message_handler("Collecting data from EFS Mount Targets...", "HEADER")

        for data in response["FileSystems"]:

            filesystem = client.describe_mount_targets(
                FileSystemId=data["FileSystemId"]
            )

            nametag = get_name_tag(data)
            filesystem_name = data["FileSystemId"] if nametag is None else nametag

            # iterate filesystems to get mount targets
            for datafilesystem in filesystem["MountTargets"]:

                # Using subnet to check VPC
                subnets = describe_subnet(
                    vpc_options=self.vpc_options, subnet_ids=datafilesystem["SubnetId"]
                )

                if subnets is not None:
                    if subnets["Subnets"][0]["VpcId"] == self.vpc_options.vpc_id:
                        digest = ResourceDigest(
                            id=data["FileSystemId"], type="aws_efs_file_system"
                        )
                        resources_found.append(
                            Resource(
                                digest=digest,
                                name=filesystem_name,
                                details="",
                                group="storage",
                                tags=resource_tags(data),
                            )
                        )
                        self.relations_found.append(
                            ResourceEdge(
                                from_node=digest,
                                to_node=ResourceDigest(
                                    id=datafilesystem["SubnetId"], type="aws_subnet"
                                ),
                            )
                        )

        return resources_found


class S3POLICY(ResourceProvider):
    def __init__(self, vpc_options: VpcOptions):
        """
        S3 policy

        :param vpc_options:
        """
        super().__init__()
        self.vpc_options = vpc_options

    @exception
    @ResourceAvailable(services="s3")
    def get_resources(self) -> List[Resource]:

        client = self.vpc_options.client("s3")

        resources_found: List[Resource] = []

        # get buckets available
        response = client.list_buckets()

        if self.vpc_options.verbose:
            message_handler("Collecting data from S3 Bucket Policies...", "HEADER")

        with ThreadPoolExecutor(15) as executor:
            results = executor.map(
                lambda data: self.analyze_bucket(client, data), response["Buckets"]
            )

        for result in results:
            if result[0] is True:
                resources_found.append(result[1])

        return resources_found

    def analyze_bucket(self, client, data):
        try:
            documentpolicy = client.get_bucket_policy(Bucket=data["Name"])
        except ClientError:
            return False, None

        document = json.dumps(documentpolicy, default=datetime_to_string)

        # check either vpc_id or potential subnet ip are found
        ipvpc_found = check_ipvpc_inpolicy(
            document=document, vpc_options=self.vpc_options
        )

        if ipvpc_found is True:
            tags_response = client.get_bucket_tagging(Bucket=data["Name"])
            digest = ResourceDigest(id=data["Name"], type="aws_s3_bucket_policy")
            self.relations_found.append(
                ResourceEdge(from_node=digest, to_node=self.vpc_options.vpc_digest())
            )
            return (
                True,
                Resource(
                    digest=digest,
                    name=data["Name"],
                    details="",
                    group="storage",
                    tags=resource_tags(tags_response),
                ),
            )
        return False, None
