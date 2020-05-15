from shared.common import *
from shared.internal.security import IAM
from shared.internal.network import VPC
import importlib, inspect
import os

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
        """"
        #....exporttf(checks)....