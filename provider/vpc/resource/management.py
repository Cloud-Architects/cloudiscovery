from provider.vpc.command import VpcOptions
from shared.common import *
from shared.error_handler import exception


class SYNTHETICSCANARIES(ResourceProvider):

    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    @exception
    def get_resources(self) -> List[Resource]:

        client = self.vpc_options.client('synthetics')

        resources_found = []

        response = client.describe_canaries()

        message_handler("Collecting data from Synthetic Canaries...", "HEADER")

        if len(response["Canaries"]) > 0:

            for data in response["Canaries"]:

                """ Check if VpcConfig is in dict """
                if "VpcConfig" in data:

                    if data['VpcConfig']['VpcId'] == self.vpc_options.vpc_id:
                        resources_found.append(Resource(digest=ResourceDigest(id=data['Id'],
                                                                              type='aws_canaries_function'),
                                                        name=data["Name"],
                                                        details='',
                                                        group='management'))

        return resources_found
