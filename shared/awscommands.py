import boto3
from shared.common import * 
from shared.internal.security import IAM, IAMPOLICY
from shared.internal.network import VPC
from shared.internal.compute import LAMBDA, EC2
from shared.internal.database import RDS, ELASTICACHE
from shared.internal.storage import EFS

class AwsCommands(object):

    def __init__(self, vpc_id, region_name):
        self.vpc_id = vpc_id
        self.region_name = region_name

    def run(self):
        IAM(self.vpc_id, self.region_name).run()
        VPC(self.vpc_id, self.region_name).run()
        LAMBDA(self.vpc_id, self.region_name).run()
        EC2(self.vpc_id, self.region_name).run()
        RDS(self.vpc_id, self.region_name).run()
        EFS(self.vpc_id, self.region_name).run()
        ELASTICACHE(self.vpc_id, self.region_name).run()
        IAMPOLICY(self.vpc_id, self.region_name).run()
