import boto3
from shared.common import * 

class VPC(object):
    
    def __init__(self, vpc_id, region_name):
        self.vpc_id = vpc_id
        self.region_name = region_name
    
    def run(self):
        try:
            client = boto3.client('ec2', region_name=self.region_name)
            response = client.describe_vpcs(
                VpcIds=[self.vpc_id]
            )

            dataresponse = response['Vpcs'][0]
            message = "VPC: {0}\nCIDR Block: {1}\nTenancy: {2}".format(self.vpc_id, 
                                                                       dataresponse['CidrBlock'], 
                                                                       dataresponse['InstanceTenancy'])
            print(message)
        except Exception as e:
            message = "There is no VpcID \"{0}\" in region {1}.\nError {2}".format(self.vpc_id, self.region_name, str(e))
            exit_critical(message)
