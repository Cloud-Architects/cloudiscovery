import boto3
from shared.common import * 

class IAM(object):
    
    def __init__(self, vpc_id, region_name):
        self.vpc_id = vpc_id
        self.region_name = region_name
    
    def run(self):
        try:
            client = boto3.client('ec2')
            
            regions = [region['RegionName'] for region in client.describe_regions()['Regions']]
            
            if self.region_name not in regions:
                message = "There is no region named: {0}".format(self.region_name)
                exit_critical(message)

        except Exception as e:
            message = "Can't connect to AWS API\nError: {0}".format(str(e))
            exit_critical(message)