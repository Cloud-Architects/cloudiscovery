from shared.common import *


class VPC(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    def run(self):
        try:
            client = self.vpc_options.client('ec2')
            response = client.describe_vpcs(
                VpcIds=[self.vpc_options.vpc_id]
            )

            dataresponse = response['Vpcs'][0]
            message = "VPC: {0}\nCIDR Block: {1}\nTenancy: {2}".format(self.vpc_options.vpc_id,
                                                                       dataresponse['CidrBlock'], 
                                                                       dataresponse['InstanceTenancy'])
            print(message)
        except Exception as e:
            message = "There is no VpcID \"{0}\" in region {1}.\nError {2}".format(self.vpc_options.vpc_id, self.vpc_options.region_name, str(e))
            exit_critical(message)
