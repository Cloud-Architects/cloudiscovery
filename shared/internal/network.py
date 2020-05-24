from shared.common import *
from shared.error_handler import exception
from typing import List

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
        message = "------------------------------------------------------\n"
        message = message + "VPC: {}\nCIDR Block: {}\nTenancy: {}\nIs default: {}".format(self.vpc_options.vpc_id,
                                                                                          dataresponse['CidrBlock'], 
                                                                                          dataresponse['InstanceTenancy'],
                                                                                          dataresponse['IsDefault'])
        print(message)

        return True

class INTERNETGATEWAY(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    @exception
    def run(self) -> List[Resource]:

        client = self.vpc_options.client('ec2')

        resources_found = []

        filters = [{'Name': 'attachment.vpc-id',
                    'Values': [self.vpc_options.vpc_id]}]

        response = client.describe_internet_gateways(Filters=filters)

        message_handler("Collecting data from INTERNET GATEWAYS...", "HEADER")

        """ One VPC has only 1 IGW then it's a direct check """
        if len(response["InternetGateways"]) > 0:

            resources_found.append(Resource(id=response['InternetGateways'][0]['InternetGatewayId'],
                                            name=response['InternetGateways'][0]['InternetGatewayId'],
                                            type='aws_internet_gateway',
                                            details=''))

        return resources_found

class NATGATEWAY(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    @exception
    def run(self) -> List[Resource]:

        client = self.vpc_options.client('ec2')

        resources_found = []

        filters = [{'Name': 'vpc-id',
                    'Values': [self.vpc_options.vpc_id]}]

        response = client.describe_nat_gateways(Filters=filters)

        message_handler("Collecting data from NAT GATEWAYS...", "HEADER")

        if len(response["NatGateways"]) > 0:

            for data in response["NatGateways"]:

                if data['VpcId'] == self.vpc_options.vpc_id:

                    resources_found.append(Resource(id=data['NatGatewayId'],
                                                    name=data['NatGatewayId'],
                                                    type='aws_nat_gateway',
                                                    details='NAT Gateway Private IP {}, Public IP {}, Subnet id {}' \
                                                    .format(data['NatGatewayAddresses'][0]['PrivateIp'],
                                                            data['NatGatewayAddresses'][0]['PublicIp'],
                                                            data['SubnetId'])))

        return resources_found

class ELASTICLOADBALANCING(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    @exception
    def run(self) -> List[Resource]:

        client = self.vpc_options.client('elb')

        resources_found = []

        response = client.describe_load_balancers()

        message_handler("Collecting data from CLASSIC LOAD BALANCING...", "HEADER")

        if len(response['LoadBalancerDescriptions']) > 0:

            for data in response['LoadBalancerDescriptions']:

                if data['VPCId'] == self.vpc_options.vpc_id:

                    resources_found.append(Resource(id=data['LoadBalancerName'],
                                                    name=data['LoadBalancerName'],
                                                    type='aws_elb_classic',
                                                    details=''))

        return resources_found

class ELASTICLOADBALANCINGV2(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    @exception
    def run(self) -> List[Resource]:

        client = self.vpc_options.client('elbv2')

        resources_found = []

        response = client.describe_load_balancers()

        message_handler("Collecting data from APPLICATION LOAD BALANCING...", "HEADER")

        if len(response['LoadBalancers']) > 0:

            for data in response['LoadBalancers']:

                if data['VpcId'] == self.vpc_options.vpc_id:
                    subnet_ids = []
                    for availabilityZone in data['AvailabilityZones']:
                        subnet_ids.append(availabilityZone['SubnetId'])

                    resources_found.append(Resource(id=data['LoadBalancerName'],
                                                    name=data['LoadBalancerName'],
                                                    type='aws_elb',
                                                    details=''))

        return resources_found

class ROUTETABLE(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    @exception
    def run(self) -> List[Resource]:

        client = self.vpc_options.client('ec2')

        resources_found = []

        filters = [{'Name': 'vpc-id',
                    'Values': [self.vpc_options.vpc_id]}]

        response = client.describe_route_tables(Filters=filters)

        message_handler("Collecting data from ROUTE TABLES...", "HEADER")

        if len(response['RouteTables']) > 0:

            """ Iterate to get all route table filtered """
            for data in response['RouteTables']:

                resources_found.append(Resource(id=data['RouteTableId'],
                                                name=data['RouteTableId'],
                                                type='aws_route_table',
                                                details=''))

        return resources_found

class SUBNET(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    @exception
    def run(self) -> List[Resource]:

        client = self.vpc_options.client('ec2')

        resources_found = []

        filters = [{'Name': 'vpc-id',
                    'Values': [self.vpc_options.vpc_id]}]

        response = client.describe_subnets(Filters=filters)

        message_handler("Collecting data from SUBNETS...", "HEADER")

        if len(response['Subnets']) > 0:

            """ Iterate to get all route table filtered """
            for data in response['Subnets']:

                resources_found.append(Resource(id=data['SubnetId'],
                                                name=data['SubnetId'],
                                                type='aws_subnet',
                                                details='Subnet using CidrBlock {} and AZ {}' \
                                                .format(data['CidrBlock'], data['AvailabilityZone'])))

        return resources_found

class NACL(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    @exception
    def run(self) -> List[Resource]:

        client = self.vpc_options.client('ec2')

        resources_found = []

        filters = [{'Name': 'vpc-id',
                    'Values': [self.vpc_options.vpc_id]}]

        response = client.describe_network_acls(Filters=filters)

        message_handler("Collecting data from NACLs...", "HEADER")

        if len(response['NetworkAcls']) > 0:

            """ Iterate to get all NACL filtered """
            for data in response['NetworkAcls']:
                subnet_ids = []
                for subnet in data['Associations']:
                    subnet_ids.append(subnet['SubnetId'])

                resources_found.append(Resource(id=data['NetworkAclId'],
                                                name=data['NetworkAclId'],
                                                type='aws_network_acl',
                                                details='NACL using Subnets {}' \
                                                .format(', '.join(subnet_ids))))

        return resources_found

class SECURITYGROUP(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    @exception
    def run(self) -> List[Resource]:

        client = self.vpc_options.client('ec2')

        resources_found = []

        filters = [{'Name': 'vpc-id',
                    'Values': [self.vpc_options.vpc_id]}]

        response = client.describe_security_groups(Filters=filters)

        message_handler("Collecting data from SECURITY GROUPS...", "HEADER")

        if len(response['SecurityGroups']) > 0:

            """ Iterate to get all SG filtered """
            for data in response['SecurityGroups']:

                resources_found.append(Resource(id=data['GroupId'],
                                                name=data['GroupName'],
                                                type='aws_security_group',
                                                details=''))


        return resources_found

class VPCPEERING(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    @exception
    def run(self) -> List[Resource]:

        client = self.vpc_options.client('ec2')

        resources_found = []

        response = client.describe_vpc_peering_connections()

        message_handler("Collecting data from VPC PEERING...", "HEADER")

        if len(response['VpcPeeringConnections']) > 0:
                
            """ Iterate to get all vpc peering and check either accepter or requester """
            for data in response['VpcPeeringConnections']:

                if data['AccepterVpcInfo']['VpcId'] == self.vpc_options.vpc_id \
                or data['RequesterVpcInfo']['VpcId'] == self.vpc_options.vpc_id:
                    
                    resources_found.append(Resource(id=data['VpcPeeringConnectionId'],
                                                    name=data['VpcPeeringConnectionId'],
                                                    type='aws_vpc_peering_connection',
                                                    details='Vpc Peering Accepter OwnerId {}, Accepter Region {}, Accepter VpcId {} \
                                                             Requester OwnerId {}, Requester Region {}, Requester VpcId' \
                                                            .format(data['AccepterVpcInfo']['OwnerId'],
                                                                    data['AccepterVpcInfo']['Region'],
                                                                    data['AccepterVpcInfo']['VpcId'],
                                                                    data['RequesterVpcInfo']['OwnerId'],
                                                                    data['RequesterVpcInfo']['Region'],
                                                                    data['RequesterVpcInfo']['VpcId'])))
        return resources_found

class VPCENDPOINT(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    @exception
    def run(self) -> List[Resource]:

        client = self.vpc_options.client('ec2')

        resources_found = []

        filters = [{'Name': 'vpc-id',
                    'Values': [self.vpc_options.vpc_id]}]

        response = client.describe_vpc_endpoints(Filters=filters)

        message_handler("Collecting data from VPC ENDPOINTS...", "HEADER")

        if len(response['VpcEndpoints']) > 0:

            """ Iterate to get all VPCE filtered """
            for data in response['VpcEndpoints']:

                if data['VpcId'] == self.vpc_options.vpc_id:
                    if data['VpcEndpointType'] == 'Gateway':
                        resources_found.append(Resource(id=data['VpcEndpointId'],
                                                        name=data['ServiceName'],
                                                        type='aws_vpc_endpoint_gateway',
                                                        details='Vpc Endpoint Gateway RouteTable {}' \
                                                        .format(', '.join(data['RouteTableIds']))))
                    else:
                        resources_found.append(Resource(id=data['VpcEndpointId'],
                                                        name=data['ServiceName'],
                                                        type='aws_vpc_endpoint_gateway',
                                                        details='Vpc Endpoint Service Subnet {}' \
                                                        .format(', '.join(data['SubnetIds']))))

        return resources_found