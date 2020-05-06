from shared.common import *
import json

class SQSPOLICY(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    def run(self):
        try:
            """ec2 = boto3.resource('ec2')
            filters = [{'Name':'vpc-id', 'Values':['vpc-017fe3c9aa3ea404d']}]
            subnets = ec2.subnets.filter(Filters=filters)
            #subnet = ec2.Subnet('subnet-023da38a98c179cce')
            for subnet in list(subnets):
                print(subnet.cidr_block)
                print(subnet)
                #free_ips = subnet.available_ip_address_count
            print(subnets)
            quit()"""

            client = self.vpc_options.session.client('sqs', region_name=self.vpc_options.region_name)
            
            response = client.list_queues()

            message_handler("\nChecking SQS QUEUE POLICY...", "HEADER")
            
            if not "QueueUrls" in response:
                message_handler("Found 0 SQS Queues in region {0}".format(self.vpc_options.region_name), "OKBLUE")
            else:
                found = 0
                message = ""

                """ SQS Queue doesn't returns a dict"""
                for idx, queue in enumerate(response["QueueUrls"]):

                    sqs_queue_policy = client.get_queue_attributes(QueueUrl=queue,
                                                                   AttributeNames=['Policy'])


                    if "Attributes" in sqs_queue_policy:

                        """ Not sure about boto3 return """
                        try:
                            documentpolicy = sqs_queue_policy['Attributes']['Policy']

                            document = json.dumps(documentpolicy, default=datetime_to_string)

                            #check_ip_inpolicy(document=document, vpc_options=self.vpc_options)
                            #print(document)
                            #quit()

                            """ check either vpc_id or potencial subnet ip are found """
                            ipvpc_found, message_ipvpc = check_ipvpc_inpolicy(document=document, vpc_options=self.vpc_options)

                            if ipvpc_found is True:
                            #if self.vpc_options.vpc_id in document:
                                found += 1
                                message = message + "\nQueueUrl: {0} - VpcId {1} - Subnet: {2}".format(
                                    queue,
                                    self.vpc_options.vpc_id,
                                    message_ipvpc
                                )
                        except Exception as e:
                            print(str(e))


                message_handler("Found {0} SQS Queue Policy using VPC {1} {2}".format(str(found), self.vpc_options.vpc_id, message),'OKBLUE')
        
        except Exception as e:
            message = "Can't list SQS Queue Policy\nError {0}".format(str(e))
            exit_critical(message)