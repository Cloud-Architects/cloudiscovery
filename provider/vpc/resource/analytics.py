import json

from provider.vpc.command import VpcOptions, check_ipvpc_inpolicy
from shared.common import *
from shared.error_handler import exception


class ELASTICSEARCH(ResourceProvider):

    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    @exception
    def get_resources(self) -> List[Resource]:

        client = self.vpc_options.client('es')

        resources_found = []

        response = client.list_domain_names()

        message_handler("Collecting data from Elasticsearch Domains...", "HEADER")

        if len(response["DomainNames"]) > 0:

            for data in response["DomainNames"]:

                elasticsearch_domain = client.describe_elasticsearch_domain(DomainName=data['DomainName'])

                documentpolicy = elasticsearch_domain['DomainStatus']['AccessPolicies']

                document = json.dumps(documentpolicy, default=datetime_to_string)

                """ check either vpc_id or potencial subnet ip are found """
                ipvpc_found = check_ipvpc_inpolicy(document=document, vpc_options=self.vpc_options)

                """ elasticsearch uses accesspolicies too, so check both situation """
                if elasticsearch_domain['DomainStatus']['VPCOptions']['VPCId'] == self.vpc_options.vpc_id \
                        or ipvpc_found is True:
                    resources_found.append(
                        Resource(digest=ResourceDigest(id=elasticsearch_domain['DomainStatus']['DomainId'],
                                                       type='aws_elasticsearch_domain'),
                                 name=elasticsearch_domain['DomainStatus']['DomainName'],
                                 details='',
                                 group='analytics'))

        return resources_found


class MSK(ResourceProvider):

    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    @exception
    def get_resources(self) -> List[Resource]:

        client = self.vpc_options.client('kafka')

        resources_found = []

        """ get all cache clusters """
        response = client.list_clusters()

        message_handler("Collecting data from MSK Clusters...", "HEADER")

        if len(response['ClusterInfoList']) > 0:

            """ iterate cache clusters to get subnet groups """
            for data in response['ClusterInfoList']:

                msk_subnets = ", ".join(data['BrokerNodeGroupInfo']['ClientSubnets'])

                ec2 = self.vpc_options.session.resource('ec2', region_name=self.vpc_options.region_name)

                filters = [{'Name': 'vpc-id',
                            'Values': [self.vpc_options.vpc_id]}]

                subnets = ec2.subnets.filter(Filters=filters)

                for subnet in list(subnets):

                    if subnet.id in msk_subnets:
                        resources_found.append(Resource(digest=ResourceDigest(id=data['ClusterArn'],
                                                                              type='aws_msk_cluster'),
                                                        name=data['ClusterName'],
                                                        details='',
                                                        group='analytics'))

                        break
        return resources_found
