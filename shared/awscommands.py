from shared.common import *
<<<<<<< HEAD
from shared.internal.security import IAM
from shared.internal.network import VPC
import importlib, inspect
import os
=======
from shared.internal.security import IAM, IAMPOLICY
from shared.internal.network import VPC, IGW, NATGATEWAY, ELB, ELBV2, ROUTETABLE, SUBNET, NACL, SG, VPCPEERING
from shared.internal.network import VPCENDPOINT
from shared.internal.compute import LAMBDA, EC2, EKS, EMR, ASG
from shared.internal.database import RDS, ELASTICACHE, DOCUMENTDB
from shared.internal.storage import EFS, S3POLICY
from shared.internal.analytics import ELASTICSEARCH, MSK
from shared.internal.application import SQSPOLICY
from shared.internal.management import CANARIES
from shared.internal.containers import ECS
>>>>>>> developer

PATH_CHECKS = "shared/internal"

class AwsCommands(object):

    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    def run(self):

        """
        The project's development pattern is a file with the respective name of the parent resource (e.g. compute, network), 
        classes of child resources inside this file and run() method to execute respective check. So it makes sense to load dynamically.

        Only IAM and VPC checks that reamins in the old way.

        TODO: improve IAM and VPC check methods
        TODO: order by resource
        """

        """ IAM and VPC validations """
        IAM(self.vpc_options).run()
        VPC(self.vpc_options).run()
        
        checks = []

        """ Iterate to get all modules """
        for name in os.listdir(PATH_CHECKS):
            if name.endswith(".py"):
                #strip the extension
                module = name[:-3]

                """ Load and call all run check """
                for nameclass, cls in inspect.getmembers(importlib.import_module("shared.internal."+module), inspect.isclass):
                    if hasattr(cls, 'run') and callable(getattr(cls, 'run')) and nameclass not in ['VPC','IAM']:
                        checks.append(cls(self.vpc_options).run())
        
<<<<<<< HEAD
        
        """ 
        TODO: Generate reports 
        """
        #....reports(checks)....

        """ 
        TODO: Generate diagrams
        """
        #....diagrams(checks)....

        """
        TODO: Export in csv/json/yaml/tf... future....
        """
        #....exporttf(checks)....
=======
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
        CANARIES(self.vpc_options).run()

        """ Containers """
        ECS(self.vpc_options).run()
>>>>>>> developer
