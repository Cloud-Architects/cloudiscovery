from shared.common import *
from shared.error_handler import exception
from typing import List


class SYNTHETICSCANARIES(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    @exception
    def run(self) -> List[Resource]:

        client = self.vpc_options.client('synthetics')

        resources_found = []
        
        response = client.describe_canaries()
        
        message_handler("Collecting data from SYNTHETICS CANARIES...", "HEADER")

        if len(response["Canaries"]) > 0:
            
            for data in response["Canaries"]:

                """ Check if VpcConfig is in dict """
                if "VpcConfig" in data:

                    if data['VpcConfig']['VpcId'] == self.vpc_options.vpc_id:

                        resources_found.append(Resource(id=data['Id'],
                                                        name=data["Name"],
                                                        type='aws_canaries_function',
                                                        details=''))

        return resources_found
