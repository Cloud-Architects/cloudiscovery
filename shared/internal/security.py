from shared.common import *
import json


class IAM(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    def run(self):
        try:
            client = self.vpc_options.session.client('ec2')
            
            regions = [region['RegionName'] for region in client.describe_regions()['Regions']]
            
            if self.vpc_options.region_name not in regions:
                message = "There is no region named: {0}".format(self.vpc_options.region_name)
                exit_critical(message)
            
        except Exception as e:
            message = "Can't connect to AWS API\nError: {0}".format(str(e))
            exit_critical(message)


class IAMPOLICY(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    def run(self):
        try:
            client = self.vpc_options.session.client('iam')

            response = client.list_policies(Scope='Local')

            message_handler("\nChecking IAM POLICY...", "HEADER")

            if len(response['Policies']) == 0:
                message_handler("Found 0 Customer managed IAM Policy", "OKBLUE")
            else:
                found = 0
                message = ""

                """ iterate policies to get document policy """
                for data in response['Policies']:

                    documentpolicy = client.get_policy_version(
                        PolicyArn=data['Arn'],
                        VersionId=data['DefaultVersionId']
                    )

                    document = json.dumps(documentpolicy, default=datetime_to_string) 

                    if self.vpc_options.vpc_id in document:
                        found += 1
                        message = message + "\nPolicyName: {0} - DefaultVersionId: {1} - VpcId: {2}".format(
                            data['PolicyName'],
                            data['DefaultVersionId'], 
                            self.vpc_options.vpc_id
                        )

                message_handler("Found {0} Customer managed IAM Policy using VPC {1} {2}".format(str(found), 
                                                                                                            self.vpc_options.vpc_id, message),
                                                                                                            'OKBLUE')
        except Exception as e:
            message = "Can't list IAM Policy\nError: {0}".format(str(e))
            exit_critical(message)