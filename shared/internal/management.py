from shared.common import *
from shared.error_handler import exception


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