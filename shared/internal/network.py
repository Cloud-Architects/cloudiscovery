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

class ELASTICLOADBALANCING(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    def run(self):

        try:
            client = self.vpc_options.client('elb')

            response = client.describe_load_balancers()

            message_handler("\nChecking CLASSIC LOAD BALANCING...", "HEADER")

            if len(response['LoadBalancerDescriptions']) == 0:
                    message_handler("Found 0 Classic Load Balancing in region {0}".format(self.vpc_options.region_name), "OKBLUE")
            else:
            
                found = 0
                message = ""

                for data in response['LoadBalancerDescriptions']:

                    if data['VPCId'] == self.vpc_options.vpc_id:

                        found += 1
                        message = message + "\nLoadBalancerName: {} -> VPC id {}".format(
                            data['LoadBalancerName'],
                            self.vpc_options.vpc_id
                            )

                message_handler("Found {0} Classic Load Balancing using VPC {1} {2}".format(str(found), self.vpc_options.vpc_id, message),'OKBLUE')

        except Exception as e:
            message = "Can't list Classic Load Balancing\nError {0}".format(str(e))
            exit_critical(message)

class ELASTICLOADBALANCINGV2(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    def run(self):

        try:
            client = self.vpc_options.client('elbv2')

            response = client.describe_load_balancers()

            message_handler("\nChecking APPLICATION LOAD BALANCING...", "HEADER")

            if len(response['LoadBalancers']) == 0:
                    message_handler("Found 0 Application Load Balancing in region {0}".format(self.vpc_options.region_name), "OKBLUE")
            else:
            
                found = 0
                message = ""

                for data in response['LoadBalancers']:

                    if data['VpcId'] == self.vpc_options.vpc_id:

                        found += 1
                        message = message + "\nLoadBalancerName: {} -> VPC id {}".format(
                            data['LoadBalancerName'],
                            self.vpc_options.vpc_id
                            )

                message_handler("Found {0} Application Load Balancing using VPC {1} {2}".format(str(found), self.vpc_options.vpc_id, message),'OKBLUE')

        except Exception as e:
            message = "Can't list Application Load Balancing\nError {0}".format(str(e))
            exit_critical(message)

class ROUTETABLE(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    def run(self):

        try:
            client = self.vpc_options.client('ec2')

            filters = [{'Name': 'vpc-id',
                        'Values': [self.vpc_options.vpc_id]}]

            response = client.describe_route_tables(Filters=filters)

            message_handler("\nChecking ROUTE TABLES...", "HEADER")

            if len(response['RouteTables']) == 0:
                    message_handler("Found 0 Route Table in region {0}".format(self.vpc_options.region_name), "OKBLUE")
            else:
            
                found = 0
                message = ""

                """ Iterate to get all route table filtered """
                for data in response['RouteTables']:

                    found += 1
                    message = message + "\nRouteTableId: {} -> VPC id {}".format(
                        data['RouteTableId'],
                        self.vpc_options.vpc_id
                        )

                message_handler("Found {0} Route Tables using VPC {1} {2}".format(str(found), self.vpc_options.vpc_id, message),'OKBLUE')

        except Exception as e:
            message = "Can't list Route Table\nError {0}".format(str(e))
            exit_critical(message)

class SUBNET(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    def run(self):

        try:
            client = self.vpc_options.client('ec2')

            filters = [{'Name': 'vpc-id',
                        'Values': [self.vpc_options.vpc_id]}]

            response = client.describe_subnets(Filters=filters)

            message_handler("\nChecking SUBNETS...", "HEADER")

            if len(response['Subnets']) == 0:
                    message_handler("Found 0 Subnets in region {0}".format(self.vpc_options.region_name), "OKBLUE")
            else:
            
                found = 0
                message = ""

                """ Iterate to get all route table filtered """
                for data in response['Subnets']:

                    found += 1
                    message = message + "\nSubnetId: {} -> VPC id {}".format(
                        data['SubnetId'],
                        self.vpc_options.vpc_id
                        )

                message_handler("Found {0} Subnets using VPC {1} {2}".format(str(found), self.vpc_options.vpc_id, message),'OKBLUE')

        except Exception as e:
            message = "Can't list Subnets\nError {0}".format(str(e))
            exit_critical(message)

class NACL(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    def run(self):

        try:
            client = self.vpc_options.client('ec2')

            filters = [{'Name': 'vpc-id',
                        'Values': [self.vpc_options.vpc_id]}]

            response = client.describe_network_acls(Filters=filters)

            message_handler("\nChecking NACLs...", "HEADER")

            if len(response['NetworkAcls']) == 0:
                    message_handler("Found 0 NACL in region {0}".format(self.vpc_options.region_name), "OKBLUE")
            else:
            
                found = 0
                message = ""

                """ Iterate to get all NACL filtered """
                for data in response['NetworkAcls']:

                    found += 1
                    message = message + "\nNetworkAclId: {} -> VPC id {}".format(
                        data['NetworkAclId'],
                        self.vpc_options.vpc_id
                        )

                message_handler("Found {0} NACL using VPC {1} {2}".format(str(found), self.vpc_options.vpc_id, message),'OKBLUE')

        except Exception as e:
            message = "Can't list NACL\nError {0}".format(str(e))
            exit_critical(message)

class SECURITYGROUP(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    def run(self):

        try:
            client = self.vpc_options.client('ec2')

            filters = [{'Name': 'vpc-id',
                        'Values': [self.vpc_options.vpc_id]}]

            response = client.describe_security_groups(Filters=filters)

            message_handler("\nChecking SECURITY GROUPS...", "HEADER")

            if len(response['SecurityGroups']) == 0:
                    message_handler("Found 0 Security Group in region {0}".format(self.vpc_options.region_name), "OKBLUE")
            else:
            
                found = 0
                message = ""

                """ Iterate to get all SG filtered """
                for data in response['SecurityGroups']:

                    found += 1
                    message = message + "\nGroupName: {} -> VPC id {}".format(
                        data['GroupName'],
                        self.vpc_options.vpc_id
                        )

                message_handler("Found {0} Security Groups using VPC {1} {2}".format(str(found), self.vpc_options.vpc_id, message),'OKBLUE')

        except Exception as e:
            message = "Can't list SECURITY GROUPS\nError {0}".format(str(e))
            exit_critical(message)

class VPCPEERING(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    def run(self):

        try:
            client = self.vpc_options.client('ec2')

            response = client.describe_vpc_peering_connections()

            message_handler("\nChecking VPC PEERING...", "HEADER")

            if len(response['VpcPeeringConnections']) == 0:
                    message_handler("Found 0 VPC Peering in region {0}".format(self.vpc_options.region_name), "OKBLUE")
            else:
            
                found = 0
                message = ""

                """ Iterate to get all vpc peering and check either accepter or requester """
                for data in response['VpcPeeringConnections']:

                    if data['AccepterVpcInfo']['VpcId'] == self.vpc_options.vpc_id \
                    or data['RequesterVpcInfo']['VpcId'] == self.vpc_options.vpc_id:
                        
                        found += 1
                        message = message + "\nVpcPeeringConnectionId: {} -> VPC id {}".format(
                            data['VpcPeeringConnectionId'],
                            self.vpc_options.vpc_id
                            )

                message_handler("Found {0} VPC Peering using VPC {1} {2}".format(str(found), self.vpc_options.vpc_id, message),'OKBLUE')

        except Exception as e:
            message = "Can't list VPC PEERING\nError {0}".format(str(e))
            exit_critical(message)

class VPCENDPOINT(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    def run(self):

        try:
            client = self.vpc_options.client('ec2')

            filters = [{'Name': 'vpc-id',
                        'Values': [self.vpc_options.vpc_id]}]

            response = client.describe_vpc_endpoints(Filters=filters)

            message_handler("\nChecking VPC ENDPOINTS...", "HEADER")

            if len(response['VpcEndpoints']) == 0:
                    message_handler("Found 0 VPC Endpoints in region {0}".format(self.vpc_options.region_name), "OKBLUE")
            else:
            
                found = 0
                message = ""

                """ Iterate to get all VPCE filtered """
                for data in response['VpcEndpoints']:

                    if data['VpcId'] == self.vpc_options.vpc_id:
                        found += 1
                        message = message + "\nVpcEndpointId: {} -> VPC id {}".format(
                            data['VpcEndpointId'],
                            self.vpc_options.vpc_id
                            )

                message_handler("Found {0} VPC Endpoints using VPC {1} {2}".format(str(found), self.vpc_options.vpc_id, message),'OKBLUE')

        except Exception as e:
            message = "Can't list VPC ENDPOINTS\nError {0}".format(str(e))
            exit_critical(message)

""" aliases """
IGW = INTERNETGATEWAY
ELB = ELASTICLOADBALANCING
ELBV2 = ELASTICLOADBALANCINGV2
SG = SECURITYGROUP