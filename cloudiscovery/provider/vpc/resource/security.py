import json
from concurrent.futures.thread import ThreadPoolExecutor
from typing import List

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
from shared.common_aws import resource_tags
from shared.error_handler import exception


class IAMPOLICY(ResourceProvider):
    def __init__(self, vpc_options: VpcOptions):
        """
        Iam policy

        :param vpc_options:
        """
        super().__init__()
        self.vpc_options = vpc_options

    @exception
    @ResourceAvailable(services="iam")
    def get_resources(self) -> List[Resource]:

        client = self.vpc_options.client("iam")

        resources_found = []

        if self.vpc_options.verbose:
            message_handler("Collecting data from IAM Policies...", "HEADER")
        paginator = client.get_paginator("list_policies")
        pages = paginator.paginate(Scope="Local")
        for policies in pages:
            with ThreadPoolExecutor(15) as executor:
                results = executor.map(
                    lambda data: self.analyze_policy(client, data), policies["Policies"]
                )
            for result in results:
                if result[0] is True:
                    resources_found.append(result[1])

        return resources_found

    def analyze_policy(self, client, data):

        documentpolicy = client.get_policy_version(
            PolicyArn=data["Arn"], VersionId=data["DefaultVersionId"]
        )

        document = json.dumps(documentpolicy, default=datetime_to_string)

        # check either vpc_id or potential subnet ip are found
        ipvpc_found = check_ipvpc_inpolicy(
            document=document, vpc_options=self.vpc_options
        )

        if ipvpc_found is True:
            digest = ResourceDigest(id=data["Arn"], type="aws_iam_policy")
            self.relations_found.append(
                ResourceEdge(from_node=digest, to_node=self.vpc_options.vpc_digest())
            )
            return (
                True,
                Resource(
                    digest=digest,
                    name=data["PolicyName"],
                    details="IAM Policy version {}".format(data["DefaultVersionId"]),
                    group="security",
                ),
            )

        return False, None


class CLOUDHSM(ResourceProvider):
    def __init__(self, vpc_options: VpcOptions):
        """
        Cloud HSM

        :param vpc_options:
        """
        super().__init__()
        self.vpc_options = vpc_options

    @exception
    @ResourceAvailable(services="cloudhsmv2")
    def get_resources(self) -> List[Resource]:

        client = self.vpc_options.client("cloudhsmv2")

        resources_found = []

        response = client.describe_clusters()

        if self.vpc_options.verbose:
            message_handler("Collecting data from CloudHSM clusters...", "HEADER")

        for data in response["Clusters"]:

            if data["VpcId"] == self.vpc_options.vpc_id:
                cloudhsm_digest = ResourceDigest(
                    id=data["ClusterId"], type="aws_cloudhsm"
                )
                resources_found.append(
                    Resource(
                        digest=cloudhsm_digest,
                        name=data["ClusterId"],
                        details="",
                        group="security",
                        tags=resource_tags(data),
                    )
                )

                for subnet in data["SubnetMapping"]:
                    subnet_id = data["SubnetMapping"][subnet]
                    self.relations_found.append(
                        ResourceEdge(
                            from_node=cloudhsm_digest,
                            to_node=ResourceDigest(id=subnet_id, type="aws_subnet"),
                        )
                    )

        return resources_found
