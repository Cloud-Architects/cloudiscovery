from shared.common import *


class LAMBDA(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    def run(self):
        try:
            client = self.vpc_options.client('lambda')
            
            response = client.list_functions()
            
            message_handler("\nChecking LAMBDA FUNCTIONS...", "HEADER")

            if len(response["Functions"]) == 0:
                message_handler("Found 0 Lambda Functions in region {0}".format(self.vpc_options.region_name), "OKBLUE")
            else:
                found = 0
                message = ""
                for data in response["Functions"]:
                    if 'VpcConfig' in data and data['VpcConfig']['VpcId'] == self.vpc_options.vpc_id:
                        found += 1
                        message = message + "\nFunctionName: {} -> Subnet id(s): {} -> VPC id {}".format(
                            data["FunctionName"],
                            ", ".join(data['VpcConfig']['SubnetIds']),
                            data['VpcConfig']['VpcId']
                        )
                message_handler("Found {0} Lambda Functions using VPC {1} {2}".format(str(found), self.vpc_options.vpc_id, message),'OKBLUE')
        except Exception as e:
            message = "Can't list Lambda Functions\nError {0}".format(str(e))
            exit_critical(message)


class EC2(object):

    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    def run(self):
        try:
            
            client = self.vpc_options.client('ec2')

            response = client.describe_instances()
            
            message_handler("\nChecking EC2 Instances...", "HEADER")

            if len(response["Reservations"]) == 0:
                message_handler("Found 0 EC2 Instances in region {0}".format(self.vpc_options.region_name), "OKBLUE")
            else:
                found = 0
                message = ""
                for data in response["Reservations"]:
                    for instances in data['Instances']:
                        if "VpcId" in instances:
                            if instances['VpcId'] == self.vpc_options.vpc_id:
                                found += 1
                                message = message + "\nInstanceId: {} - PrivateIpAddress: {} -> Subnet id(s): {} - VpcId {}".format(
                                    instances["InstanceId"], 
                                    instances["PrivateIpAddress"], 
                                    instances['SubnetId'],
                                    instances['VpcId']
                                )
                message_handler("Found {0} EC2 Instances using VPC {1} {2}".format(str(found), self.vpc_options.vpc_id, message),'OKBLUE')
        except Exception as e:
            message = "Can't list EC2 Instances\nError {0}".format(str(e))
            exit_critical(message)

class EKS(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    def run(self):
        try:
            client = self.vpc_options.client('eks')
            
            response = client.list_clusters()
            
            message_handler("\nChecking EKS CLUSTERS...", "HEADER")

            if len(response["clusters"]) == 0:
                message_handler("Found 0 EKS Clusters in region {0}".format(self.vpc_options.region_name), "OKBLUE")
            else:
                found = 0
                message = ""
                for data in response["clusters"]:

                    cluster = client.describe_cluster(name=data)

                    if cluster['cluster']['resourcesVpcConfig']['vpcId'] == self.vpc_options.vpc_id:
                        found += 1
                        message = message + "\ncluster: {} - VpcId {}".format(
                            data, 
                            self.vpc_options.vpc_id
                        )

                message_handler("Found {0} EKS Clusters using VPC {1} {2}".format(str(found), self.vpc_options.vpc_id, message),'OKBLUE')
        
        except Exception as e:
            message = "Can't list EKS Clusters\nError {0}".format(str(e))
            exit_critical(message)

class EMR(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    def run(self):
        try:
            client = self.vpc_options.client('emr')
            
            response = client.list_clusters()

            message_handler("\nChecking EMR CLUSTERS...", "HEADER")

            if len(response["Clusters"]) == 0:
                message_handler("Found 0 EMR Clusters in region {0}".format(self.vpc_options.region_name), "OKBLUE")
            else:
                found = 0
                message = ""
                for data in response["Clusters"]:

                    cluster = client.describe_cluster(ClusterId=data['Id'])

                    """ Using subnet to check VPC """
                    ec2 = self.vpc_options.client('ec2')
                        
                    subnets = ec2.describe_subnets(SubnetIds=[cluster['Cluster']['Ec2InstanceAttributes']['Ec2SubnetId']])


                    if subnets['Subnets'][0]['VpcId'] == self.vpc_options.vpc_id:
                        found += 1
                        message = message + "\nClusterId: {} - VpcId {}".format(
                            data['Id'], 
                            self.vpc_options.vpc_id
                        )

                message_handler("Found {0} EMR Clusters using VPC {1} {2}".format(str(found), self.vpc_options.vpc_id, message),'OKBLUE')
        
        except Exception as e:
            message = "Can't list EMR Clusters\nError {0}".format(str(e))
            exit_critical(message)