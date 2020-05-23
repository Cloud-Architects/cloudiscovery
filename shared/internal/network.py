from shared.common import *
from shared.error_handler import exception

class VPC(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    @exception
    def run(self):

        client = self.vpc_options.client('ec2')
        response = client.describe_vpcs(
            VpcIds=[self.vpc_options.vpc_id]
        )

        dataresponse = response['Vpcs'][0]
        message = "VPC: {}\nCIDR Block: {}\nTenancy: {}\nIs default: {}".format(self.vpc_options.vpc_id,
                                                                    dataresponse['CidrBlock'], 
                                                                    dataresponse['InstanceTenancy'],
                                                                    dataresponse['IsDefault'])
        print(message)

        return True

class INTERNETGATEWAY(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    @exception
    def run(self):

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

        return True

class NATGATEWAY(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    @exception
    def run(self):

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
                    message = message + "\nNatGatewayId: {} -> Private IP {} - Public IP {} -> Subnet Id: {} -> VPC id {}".format(
                        data['NatGatewayId'],
                        data['NatGatewayAddresses'][0]['PrivateIp'],
                        data['NatGatewayAddresses'][0]['PublicIp'],
                        data['SubnetId'],
                        self.vpc_options.vpc_id
                        )

            message_handler("Found {0} NAT Gateways using VPC {1} {2}".format(str(found), self.vpc_options.vpc_id, message),'OKBLUE')

        return True

class ELASTICLOADBALANCING(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    @exception
    def run(self):

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
                    message = message + "\nLoadBalancerName: {} - Subnet id: {} -> VPC id {}".format(
                        data['LoadBalancerName'],
                        ', '.join(data['Subnets']),
                        self.vpc_options.vpc_id
                        )

            message_handler("Found {0} Classic Load Balancing using VPC {1} {2}".format(str(found), self.vpc_options.vpc_id, message),'OKBLUE')

        return True

class ELASTICLOADBALANCINGV2(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    @exception
    def run(self):

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
                    subnet_ids = []
                    for availabilityZone in data['AvailabilityZones']:
                        subnet_ids.append(availabilityZone['SubnetId'])

                    found += 1
                    message = message + "\nLoadBalancerName: {} -> VPC id {}".format(
                        data['LoadBalancerName'],
                        ', '.join(subnet_ids),
                        self.vpc_options.vpc_id
                        )

            message_handler("Found {0} Application Load Balancing using VPC {1} {2}".format(str(found), self.vpc_options.vpc_id, message),'OKBLUE')

        return True

class ROUTETABLE(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    @exception
    def run(self):

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

        return True

class SUBNET(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    @exception
    def run(self):

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
                message = message + "\nSubnetId: {} - CIDR block: {} - AZ: {} -> VPC id {}".format(
                    data['SubnetId'],
                    data['CidrBlock'],
                    data['AvailabilityZone'],
                    self.vpc_options.vpc_id
                    )

            message_handler("Found {0} Subnets using VPC {1} {2}".format(str(found), self.vpc_options.vpc_id, message),'OKBLUE')

        return True

class NACL(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    @exception
    def run(self):

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
                subnet_ids = []
                for subnet in data['Associations']:
                    subnet_ids.append(subnet['SubnetId'])

                found += 1
                message = message + "\nNetworkAclId: {} -> Subnet Id: {} -> VPC Id: {}".format(
                    data['NetworkAclId'],
                    ', '.join(subnet_ids),
                    self.vpc_options.vpc_id
                    )

            message_handler("Found {0} NACL using VPC {1} {2}".format(str(found), self.vpc_options.vpc_id, message),'OKBLUE')

        return True

class SECURITYGROUP(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    @exception
    def run(self):

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

        return True

class VPCPEERING(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    @exception
    def run(self):

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
                    message = message + "\nVpcPeeringConnectionId: {} -> Owner: {} - Region: {} - Requester VPC id: {} -> Owner: {} - Region: {} - Accepter VPC id: {}".format(
                        data['VpcPeeringConnectionId'],
                        data['AccepterVpcInfo']['OwnerId'],
                        data['AccepterVpcInfo']['Region'],
                        data['AccepterVpcInfo']['VpcId'],
                        data['RequesterVpcInfo']['OwnerId'],
                        data['RequesterVpcInfo']['Region'],
                        data['RequesterVpcInfo']['VpcId']
                        )

            message_handler("Found {0} VPC Peering using VPC {1} {2}".format(str(found), self.vpc_options.vpc_id, message),'OKBLUE')

        return True

class VPCENDPOINT(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    @exception
    def run(self):

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
                    if data['VpcEndpointType'] == 'Gateway':
                        message = message + "\nGateway VpcEndpointId: {} - Service: {} -> Route table Id: {} -> VPC id: {}".format(
                            data['VpcEndpointId'],
                            data['ServiceName'],
                            ', '.join(data['RouteTableIds']),
                            self.vpc_options.vpc_id
                            )
                    else:
                        message = message + "\nInterface VpcEndpointId: {} - Service: {} -> Subnet Id: {} -> VPC id: {}".format(
                            data['VpcEndpointId'],
                            data['ServiceName'],
                            ', '.join(data['SubnetIds']),
                            self.vpc_options.vpc_id
                            )

            message_handler("Found {0} VPC Endpoints using VPC {1} {2}".format(str(found), self.vpc_options.vpc_id, message),'OKBLUE')

        return True

""" aliases """
IGW = INTERNETGATEWAY
ELB = ELASTICLOADBALANCING
ELBV2 = ELASTICLOADBALANCINGV2
SG = SECURITYGROUP