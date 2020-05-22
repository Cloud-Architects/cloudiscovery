from shared.common import *
from shared.internal.security import IAM, IAMPOLICY
from shared.internal.network import VPC, IGW, NATGATEWAY, ELB, ELBV2, ROUTETABLE, SUBNET, NACL, SG, VPCPEERING
from shared.internal.network import VPCENDPOINT
from shared.internal.compute import LAMBDA, EC2, EKS, EMR, ASG
from shared.internal.database import RDS, ELASTICACHE, DOCUMENTDB
from shared.internal.storage import EFS, S3POLICY
from shared.internal.analytics import ELASTICSEARCH, MSK
from shared.internal.application import SQSPOLICY
from shared.internal.management import CLOUDFORMATION, CANARIES
from shared.internal.containers import ECS


class AwsCommands(object):

    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    def run(self):

        """ IAM and VPC validations """
        IAM(self.vpc_options).run()
        VPC(self.vpc_options).run()

        """ Compute resources """
        EC2(self.vpc_options).run()
        LAMBDA(self.vpc_options).run()
        EKS(self.vpc_options).run()
        EMR(self.vpc_options).run()
        ASG(self.vpc_options).run()

        """ Database resources """
        RDS(self.vpc_options).run()
        ELASTICACHE(self.vpc_options).run()
        DOCUMENTDB(self.vpc_options).run()

        """ Application resources """
        SQSPOLICY(self.vpc_options).run()

        """ Storage resources """
        EFS(self.vpc_options).run()
        S3POLICY(self.vpc_options).run()
        
        """ Analytics resources """
        ELASTICSEARCH(self.vpc_options).run()
        MSK(self.vpc_options).run()

        """ Security resources """
        IAMPOLICY(self.vpc_options).run()
        
        """ Network resources """
        IGW(self.vpc_options).run()
        NATGATEWAY(self.vpc_options).run()
        ELB(self.vpc_options).run()
        ELBV2(self.vpc_options).run()
        ROUTETABLE(self.vpc_options).run()
        SUBNET(self.vpc_options).run()
        NACL(self.vpc_options).run()
        SG(self.vpc_options).run()
        VPCPEERING(self.vpc_options).run()
        VPCENDPOINT(self.vpc_options).run()

        """ Management resources """
        CLOUDFORMATION(self.vpc_options).run()
        CANARIES(self.vpc_options).run()

        """ Containers """
        ECS(self.vpc_options).run()
        