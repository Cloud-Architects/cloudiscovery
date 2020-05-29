from provider.vpc.command import VpcOptions, check_ipvpc_inpolicy
from shared.common import *
from shared.error_handler import exception
from typing import List
import json

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

class MEDIALIVE(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    @exception
    def run(self) -> List[Resource]:
 
        client = self.vpc_options.client('medialive')

        resources_found = []
        
        response = client.list_inputs()

        message_handler("Collecting data from MEDIA LIVE INPUTS...", "HEADER")

        if len(response['Inputs']) > 0:
            
            for data in response["Inputs"]:
                for destinations in data['Destinations']:
                    if "Vpc" in destinations:
                        """ describe networkinterface to get VpcId """
                        ec2 = self.vpc_options.client('ec2')

                        eni = ec2.describe_network_interfaces(NetworkInterfaceIds=[destinations["Vpc"]['NetworkInterfaceId']])

                        if eni['NetworkInterfaces'][0]['VpcId'] == self.vpc_options.vpc_id:

                            resources_found.append(Resource(id=data['Arn'],
                                                            name="Input " + destinations["Ip"],
                                                            type='aws_media_live',
                                                            details='',
                                                            group='mediaservices'))
        return resources_found

class MEDIASTORE(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    @exception
    def run(self) -> List[Resource]:
 
        client = self.vpc_options.client('mediastore')

        resources_found = []
        
        response = client.list_containers()

        message_handler("Collecting data from MEDIA STORE...", "HEADER")

        if len(response['Containers']) > 0:
            
            for data in response['Containers']:

                store_queue_policy = client.get_container_policy(ContainerName=data["Name"])

                document = json.dumps(store_queue_policy["Policy"], default=datetime_to_string)

                ipvpc_found = check_ipvpc_inpolicy(document=document, vpc_options=self.vpc_options)

                if ipvpc_found is not False:

                        resources_found.append(Resource(id=data['ARN'],
                                                        name=data["Name"],
                                                        type='aws_mediastore_polocy',
                                                        details='',
                                                        group='mediaservices'))
        return resources_found
