import json
from concurrent.futures.thread import ThreadPoolExecutor
from typing import List

from shared.common import *
from shared.error_handler import exception


class IAM(object):

    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    @exception
    def run(self):
        client = self.vpc_options.session.client('ec2')

        regions = [region['RegionName'] for region in client.describe_regions()['Regions']]

        if self.vpc_options.region_name not in regions:
            message = "There is no region named: {0}".format(self.vpc_options.region_name)
            exit_critical(message)

        return True


class IAMPOLICY(object):

    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    @exception
    def run(self) -> List[Resource]:

        client = self.vpc_options.session.client('iam')

        resources_found = []

        response = client.list_policies(Scope='Local')

        message_handler("Collecting data from IAM POLICY...", "HEADER")

        if len(response['Policies']) == 0:
            message_handler("Found 0 Customer managed IAM Policy", "OKBLUE")
        else:
            found = 0
            message = ""

            with ThreadPoolExecutor(15) as executor:
                results = executor.map(lambda data: self.analyze_policy(client, data), response['Policies'])
            for result in results:
                if result[0] is True:
                    resources_found.append(result[1])

        return resources_found

    def analyze_policy(self, client, data):

        documentpolicy = client.get_policy_version(
            PolicyArn=data['Arn'],
            VersionId=data['DefaultVersionId']
        )

        document = json.dumps(documentpolicy, default=datetime_to_string)

        """ check either vpc_id or potencial subnet ip are found """
        ipvpc_found = check_ipvpc_inpolicy(document=document, vpc_options=self.vpc_options)

        if ipvpc_found is True:
            return True, Resource(id=data['Arn'],
                                  name=data['PolicyName'],
                                  type='aws_iam_policy',
                                  details='IAM Policy version {}'.format(data['DefaultVersionId']),
                                  group='security')

        return False, None
