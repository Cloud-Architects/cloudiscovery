from shared.awscommands import *
from shared.common import *
import boto3

class Vpc(object):

    def __init__(self, vpc_id, region_name):
        self.vpc_id = vpc_id
        self.region_name = region_name

    def run(self):

        """ aws profile check """
        access_key, secret_key, region_name = check_aws_profile()

        if self.region_name is None and region_name is None:
            exit_critical("Neither region parameter or region config were informed")
        
        """ assuming region parameter precedes region configuration """
        if self.region_name is not None:
            region_name = self.region_name
        
        """ init class awscommands """
        awscommands = AwsCommands(vpc_id=self.vpc_id, region_name=region_name)
        awscommands.run()


