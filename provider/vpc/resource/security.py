import json
from concurrent.futures.thread import ThreadPoolExecutor

from provider.vpc.command import VpcOptions, check_ipvpc_inpolicy
from shared.common import *
from shared.error_handler import exception


class IAMPOLICY(ResourceProvider):

    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    @exception
    def get_resources(self) -> List[Resource]:

        client = self.vpc_options.session.client('iam')

        resources_found = []

        message_handler("Collecting data from IAM Policies...", "HEADER")
        paginator = client.get_paginator('list_policies')
        pages = paginator.paginate(
            Scope='Local'
        )
        for policies in pages:
            with ThreadPoolExecutor(15) as executor:
                results = executor.map(lambda data: self.analyze_policy(client, data), policies['Policies'])
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

        """ check either vpc_id or potential subnet ip are found """
        ipvpc_found = check_ipvpc_inpolicy(document=document, vpc_options=self.vpc_options)

        if ipvpc_found is True:
            return True, Resource(digest=ResourceDigest(id=data['Arn'], type='aws_iam_policy'),
                                  name=data['PolicyName'],
                                  details='IAM Policy version {}'.format(data['DefaultVersionId']),
                                  group='security')

        return False, None
