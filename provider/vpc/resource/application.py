import json
from concurrent.futures.thread import ThreadPoolExecutor
from typing import List

from provider.vpc.command import VpcOptions, check_ipvpc_inpolicy
from shared.common import *
from shared.error_handler import exception


class SQSPOLICY(object):

    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    @exception
    def run(self) -> List[Resource]:

        client = self.vpc_options.client('sqs')

        resources_found = []

        response = client.list_queues()

        message_handler("Collecting data from SQS QUEUE POLICY...", "HEADER")

        if "QueueUrls" in response:

            with ThreadPoolExecutor(15) as executor:
                results = executor.map(lambda data: self.analyze_queues(client, data[1]),
                                       enumerate(response["QueueUrls"]))

            for result in results:

                if result[0] is True:
                    resources_found.append(result[1])

        return resources_found

    @exception
    def analyze_queues(self, client, queue):

        sqs_queue_policy = client.get_queue_attributes(QueueUrl=queue, AttributeNames=['QueueArn', 'Policy'])

        if "Attributes" in sqs_queue_policy:

            if "Policy" in sqs_queue_policy['Attributes']:

                documentpolicy = sqs_queue_policy['Attributes']['Policy']
                queuearn = sqs_queue_policy['Attributes']['QueueArn']
                document = json.dumps(documentpolicy, default=datetime_to_string)

                """ check either vpc_id or potencial subnet ip are found """
                ipvpc_found = check_ipvpc_inpolicy(document=document, vpc_options=self.vpc_options)

                if ipvpc_found is not False:
                    return True, Resource(id=queuearn,
                                          name=queue,
                                          type='aws_sqs_queue_policy',
                                          details='',
                                          group='application')

        return False, None
