from concurrent.futures.thread import ThreadPoolExecutor
from shared.error_handler import exception
from shared.common import *
import json


class SQSPOLICY(object):

    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    @exception
    def run(self):
        
        client = self.vpc_options.client('sqs')

        response = client.list_queues()
       
        message_handler("\nChecking SQS QUEUE POLICY...", "HEADER")

        if "QueueUrls" not in response:
            message_handler("Found 0 SQS Queues in region {0}".format(self.vpc_options.region_name), "OKBLUE")
        else:
            found = 0
            message = ""

            with ThreadPoolExecutor(15) as executor:
                results = executor.map(lambda data: self.analyze_queues(client, data[1]), enumerate(response["QueueUrls"]))

            for result in results:
                if result[0] is True:
                    found += 1
                    message += result[1]
            message_handler("Found {0} SQS Queue Policy using VPC {1} {2}".format(str(found), self.vpc_options.vpc_id, message),'OKBLUE')

        return True
        
    @exception
    def analyze_queues(self, client, queue):

        sqs_queue_policy = client.get_queue_attributes(QueueUrl=queue, AttributeNames=['Policy'])
        if "Attributes" in sqs_queue_policy:

            """ Not sure about boto3 return """

            documentpolicy = sqs_queue_policy['Attributes']['Policy']
            document = json.dumps(documentpolicy, default=datetime_to_string)

            """ check either vpc_id or potencial subnet ip are found """
            ipvpc_found = check_ipvpc_inpolicy(document=document, vpc_options=self.vpc_options)

            if ipvpc_found is not False:
                return True, "\nQueueUrl: {0} -> {1} -> VPC {2}".format(
                    queue,
                    ipvpc_found,
                    self.vpc_options.vpc_id
                )

        return False, None
