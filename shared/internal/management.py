from shared.common import *
import json
from shared.error_handler import exception

class CLOUDFORMATION(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    @exception
    def run(self):

        client = self.vpc_options.client('cloudformation')
        
        response = client.describe_stacks()
        
        message_handler("\nChecking CLOUDFORMATION STACKS...", "HEADER")

        if len(response["Stacks"]) == 0:
            message_handler("Found 0 Cloudformation Stacks in region {0}".format(self.vpc_options.region_name), "OKBLUE")
        else:
            found = 0
            message = ""
            for data in response["Stacks"]:

                template = client.get_template(StackName=data['StackName'])

                documenttemplate = template['TemplateBody']

                document = json.dumps(documenttemplate, default=datetime_to_string)

                """ check either vpc_id or potencial subnet ip are found """
                ipvpc_found = check_ipvpc_inpolicy(document=document, vpc_options=self.vpc_options)

                """ elasticsearch uses accesspolicies too, so check both situation """
                if ipvpc_found is True:
                    found += 1
                    message = message + "\nStackName: {} -> VpcId {}".format(
                        data['StackName'], 
                        self.vpc_options.vpc_id
                    )

            message_handler("Found {0} Cloudformation Stacks using VPC {1} {2}".format(str(found), self.vpc_options.vpc_id, message),'OKBLUE')
        
        return True

class SYNTHETICSCANARIES(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    @exception
    def run(self):

        client = self.vpc_options.client('synthetics')
        
        response = client.describe_canaries()
        
        message_handler("\nChecking SYNTHETICS CANARIES...", "HEADER")

        if len(response["Canaries"]) == 0:
            message_handler("Found 0 Synthetic Canaries in region {0}".format(self.vpc_options.region_name), "OKBLUE")
        else:
            found = 0
            message = ""
            for data in response["Canaries"]:

                """ Check if VpcConfig is in dict """
                if "VpcConfig" in data:

                    if data['VpcConfig']['VpcId'] == self.vpc_options.vpc_id:
                        found += 1
                        message = message + "\nCanariesName: {} -> VpcId {}".format(
                            data['Name'], 
                            self.vpc_options.vpc_id
                        )

            message_handler("Found {0} Synthetic Canaries using VPC {1} {2}".format(str(found), self.vpc_options.vpc_id, message),'OKBLUE')

        return True

CANARIES = SYNTHETICSCANARIES