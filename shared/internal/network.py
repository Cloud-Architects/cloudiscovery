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

class INTERNETGATEWAY(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    def run(self):

        try:
            client = self.vpc_options.client('ec2')

            filters = [{'Name': 'attachment.vpc-id',
                        'Values': [self.vpc_options.vpc_id]}]

            response = client.describe_internet_gateways(Filters=filters)

            message_handler("\nChecking INTERNET GATEWAYS...", "HEADER")

            """ One VPC has only 1 IGW then it's a direct check """
            if len(response["InternetGateways"]) == 0:
                    message_handler("Found 0 Internet Gateway in region {0}".format(self.vpc_options.region_name), "OKBLUE")
            else:
            
                found = 1

                message = "\nInternetGatewayId: {} -> VPC id {}".format(
                            response['InternetGateways'][0]['InternetGatewayId'],
                            self.vpc_options.vpc_id
                            )
                
                message_handler("Found {0} Internet Gateway using VPC {1} {2}".format(str(found), \
                                                                                    self.vpc_options.vpc_id, message), \
                                                                                    'OKBLUE')

        except Exception as e:
            message = "Can't list Internet Gateway\nError {0}".format(str(e))
            exit_critical(message)


class NATGATEWAY(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    def run(self):

        try:
            client = self.vpc_options.client('ec2')

            filters = [{'Name': 'vpc-id',
                        'Values': [self.vpc_options.vpc_id]}]

            response = client.describe_nat_gateways(Filters=filters)

            message_handler("\nChecking NAT GATEWAYS...", "HEADER")

            if len(response["NatGateways"]) == 0:
                    message_handler("Found 0 NAT Gateways in region {0}".format(self.vpc_options.region_name), "OKBLUE")
            else:
            
                found = 0
                message = ""

                for data in response["NatGateways"]:

                    if data['VpcId'] == self.vpc_options.vpc_id:

                        found += 1
                        message = message + "\nNatGatewayId: {} -> VPC id {}".format(
                            data['NatGatewayId'],
                            self.vpc_options.vpc_id
                            )

                message_handler("Found {0} NAT Gateways using VPC {1} {2}".format(str(found), self.vpc_options.vpc_id, message),'OKBLUE')

        except Exception as e:
            message = "Can't list NAT Gateways\nError {0}".format(str(e))
            exit_critical(message)

""" alias """
IGW = INTERNETGATEWAY