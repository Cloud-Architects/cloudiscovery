from shared.common import *
from shared.error_handler import exception
from typing import List

class MEDIACONNECT(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    @exception
    def run(self) -> List[Resource]:
 
        client = self.vpc_options.client('mediaconnect')

        resources_found = []
        
        response = client.list_flows()

        message_handler("Collecting data from MEDIA CONNECT...", "HEADER")

        if len(response['Flows']) > 0:
            
            for data in response["Flows"]:

                data_flow = client.describe_flow(FlowArn=data['FlowArn'])

                if "VpcInterfaces" in data_flow["Flow"]:

                    for data_interfaces in data_flow["Flow"]["VpcInterfaces"]:

                        """ describe subnet to get VpcId """
                        ec2 = self.vpc_options.client('ec2')

                        subnets = ec2.describe_subnets(SubnetIds=[data_interfaces['SubnetId']])

                        if subnets['Subnets'][0]['VpcId'] == self.vpc_options.vpc_id:

                            resources_found.append(Resource(id=data['FlowArn'],
                                                            name=data['Name'],
                                                            type='aws_media_connect',
                                                            details='Flow using VPC {} in VPC Interface {}'\
                                                            .format(self.vpc_options.vpc_id, data_interfaces['Name']),
                                                            group='mediaservices'))

        return resources_found

