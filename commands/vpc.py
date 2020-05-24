from shared.awscommands import *
from shared.common import *


class Vpc(object):

    def __init__(self, vpc_id, region_name, profile_name):
        self.vpc_id = vpc_id
        self.region_name = region_name
        self.profile_name = profile_name

    def run(self):

        """ aws profile check """
        session = generate_session(self.profile_name)
        session.get_credentials()
        region_name = session.region_name

        if self.region_name is None and region_name is None:
            exit_critical(_("Neither region parameter or region config were informed"))

        """ assuming region parameter precedes region configuration """
        if self.region_name is not None:
            region_name = self.region_name

        """ if vpc is none, get all vpcs and check """
        if self.vpc_id is None:
            client = session.client('ec2')
            vpcs = client.describe_vpcs()
            for data in vpcs['Vpcs']:
                """ init class awscommands """
                awscommands = AwsCommands(VpcOptions(session=session, vpc_id=data['VpcId'], region_name=region_name)).run()
        else:
            """ init class awscommands """
            awscommands = AwsCommands(VpcOptions(session=session, vpc_id=self.vpc_id, region_name=region_name)).run()


        


