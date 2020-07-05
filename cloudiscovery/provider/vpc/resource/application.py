import json
from concurrent.futures.thread import ThreadPoolExecutor
from typing import List

from provider.vpc.command import VpcOptions, check_ipvpc_inpolicy
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


class SQSPOLICY(ResourceProvider):
    def __init__(self, vpc_options: VpcOptions):
        """
        Sqs policy

        :param vpc_options:
        """
        super().__init__()
        self.vpc_options = vpc_options

    @exception
    @ResourceAvailable(services="sqs")
    def get_resources(self) -> List[Resource]:

        client = self.vpc_options.client("sqs")

        resources_found = []

        response = client.list_queues()

        if self.vpc_options.verbose:
            message_handler("Collecting data from SQS Queue Policy...", "HEADER")

        if "QueueUrls" in response:

            with ThreadPoolExecutor(15) as executor:
                results = executor.map(
                    lambda data: self.analyze_queues(client, data[1]),
                    enumerate(response["QueueUrls"]),
                )

            for result in results:

                if result[0] is True:
                    resources_found.append(result[1])

        return resources_found

    @exception
    def analyze_queues(self, client, queue):

        sqs_queue_policy = client.get_queue_attributes(
            QueueUrl=queue, AttributeNames=["QueueArn", "Policy"]
        )

        if "Attributes" in sqs_queue_policy:

            if "Policy" in sqs_queue_policy["Attributes"]:

                documentpolicy = sqs_queue_policy["Attributes"]["Policy"]
                queuearn = sqs_queue_policy["Attributes"]["QueueArn"]
                document = json.dumps(documentpolicy, default=datetime_to_string)

                # check either vpc_id or potencial subnet ip are found
                ipvpc_found = check_ipvpc_inpolicy(
                    document=document, vpc_options=self.vpc_options
                )

                if ipvpc_found is not False:
                    list_tags_response = client.list_queue_tags(QueueUrl=queue)
                    resource_digest = ResourceDigest(
                        id=queuearn, type="aws_sqs_queue_policy"
                    )
                    self.relations_found.append(
                        ResourceEdge(
                            from_node=resource_digest,
                            to_node=self.vpc_options.vpc_digest(),
                        )
                    )
                    return (
                        True,
                        Resource(
                            digest=resource_digest,
                            name=queue,
                            details="",
                            group="application",
                            tags=resource_tags(list_tags_response),
                        ),
                    )

        return False, None
