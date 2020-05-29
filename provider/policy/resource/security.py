from concurrent.futures.thread import ThreadPoolExecutor
from typing import List

from provider.policy.command import ProfileOptions
from shared.common import *
from shared.error_handler import exception


class IAMPOLICY(object):

    def __init__(self, options: ProfileOptions):
        self.options = options

    @exception
    def run(self) -> List[Resource]:

        client = self.options.session.client('iam')

        resources_found = []

        message_handler("Collecting data from IAM POLICY...", "HEADER")
        paginator = client.get_paginator('list_policies')
        pages = paginator.paginate(
            Scope='Local'
        )
        for policies in pages:
            with ThreadPoolExecutor(15) as executor:
                results = executor.map(lambda data: self.analyze_policy(data), policies['Policies'])
            for result in results:
                if result[0] is True:
                    resources_found.append(result[1])

        return resources_found

    def analyze_policy(self, data):
        return True, Resource(id=data['Arn'],
                              name=data['PolicyName'],
                              type='aws_iam_policy',
                              details='IAM Policy version {}'.format(data['DefaultVersionId']),
                              group='security')
