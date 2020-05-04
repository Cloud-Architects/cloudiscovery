from shared.common import *
from shared.internal.security import IAM, IAMPOLICY
from shared.internal.network import VPC
from shared.internal.compute import LAMBDA, EC2
from shared.internal.database import RDS, ELASTICACHE
from shared.internal.storage import EFS, S3POLICY
from shared.internal.analytics import ELASTICSEARCH


class AwsCommands(object):

    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    def run(self):
        IAM(self.vpc_options).run()
        VPC(self.vpc_options).run()
        LAMBDA(self.vpc_options).run()
        EC2(self.vpc_options).run()
        RDS(self.vpc_options).run()
        EFS(self.vpc_options).run()
        ELASTICACHE(self.vpc_options).run()
        IAMPOLICY(self.vpc_options).run()
        S3POLICY(self.vpc_options).run()
        ELASTICSEARCH(self.vpc_options).run()
