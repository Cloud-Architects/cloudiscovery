from shared.common import *
from shared.internal.security import IAM, IAMPOLICY
from shared.internal.network import VPC, IGW, NATGATEWAY, ELB, ELBV2, ROUTETABLE, SUBNET, NACL
from shared.internal.compute import LAMBDA, EC2
from shared.internal.database import RDS, ELASTICACHE, DOCUMENTDB
from shared.internal.storage import EFS, S3POLICY
from shared.internal.analytics import ELASTICSEARCH, MSK
from shared.internal.application import SQSPOLICY


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
        DOCUMENTDB(self.vpc_options).run()
        SQSPOLICY(self.vpc_options).run()
        MSK(self.vpc_options).run()
        IGW(self.vpc_options).run()
        NATGATEWAY(self.vpc_options).run()
        ELB(self.vpc_options).run()
        ELBV2(self.vpc_options).run()
        ROUTETABLE(self.vpc_options).run()
        SUBNET(self.vpc_options).run()
        NACL(self.vpc_options).run()