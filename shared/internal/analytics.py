from shared.common import *
import json

class ELASTICSEARCH(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    def run(self):
        try:
            client = self.vpc_options.session.client('es', region_name=self.vpc_options.region_name)
            
            response = client.list_domain_names()
            
            message_handler("\nChecking ELASTICSEARCH DOMAINS...", "HEADER")

            if len(response["DomainNames"]) == 0:
                message_handler("Found 0 Elastic Search Domains in region {0}".format(self.vpc_options.region_name), "OKBLUE")
            else:
                found = 0
                message = ""
                for data in response["DomainNames"]:

                    elasticsearch_domain = client.describe_elasticsearch_domain(DomainName=data['DomainName'])

                    documentpolicy = elasticsearch_domain['DomainStatus']['AccessPolicies']

                    document = json.dumps(documentpolicy, default=datetime_to_string)

                    """ check either vpc_id or potencial subnet ip are found """
                    ipvpc_found = check_ipvpc_inpolicy(document=document, vpc_options=self.vpc_options)

                    """ elasticsearch uses accesspolicies too, so check both situation """
                    if elasticsearch_domain['DomainStatus']['VPCOptions']['VPCId'] == self.vpc_options.vpc_id \
                    or ipvpc_found is True:
                        found += 1
                        message = message + "\nDomainId: {0} - DomainName: {1} - VpcId {2}".format(
                            elasticsearch_domain['DomainStatus']['DomainId'], 
                            elasticsearch_domain['DomainStatus']['DomainName'], 
                            self.vpc_options.vpc_id
                        )
                message_handler("Found {0} ElasticSearch Domains using VPC {1} {2}".format(str(found), self.vpc_options.vpc_id, message),'OKBLUE')
        
        except Exception as e:
            message = "Can't list ElasticSearch Domains\nError {0}".format(str(e))
            exit_critical(message)

class MSK(object):

    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    def run(self):
        try:
            client = self.vpc_options.session.client('kafka', region_name=self.vpc_options.region_name)

            """ get all cache clusters """
            response = client.list_clusters()

            message_handler("\nChecking MSK CLUSTERS...", "HEADER")

            if len(response['ClusterInfoList']) == 0:
                message_handler("Found 0 MSK Clusters in region {0}".format(self.vpc_options.region_name), "OKBLUE")
            else:
                found = 0
                message = ""

                """ iterate cache clusters to get subnet groups """
                for data in response['ClusterInfoList']:

                    msk_subnets = ", ".join(data['BrokerNodeGroupInfo']['ClientSubnets'])

                    ec2 = self.vpc_options.session.resource('ec2', region_name=self.vpc_options.region_name)

                    filters = [{'Name':'vpc-id',
                                'Values':[self.vpc_options.vpc_id]}]

                    subnets = ec2.subnets.filter(Filters=filters)

                    for subnet in list(subnets):

                        if subnet.id in msk_subnets:

                            found += 1
                            message = message + "\nClusterName: {0} - VpcId: {1}".format(
                                data['ClusterName'],
                                self.vpc_options.vpc_id
                            )
                            break

                message_handler("Found {0} MSK Clusters using VPC {1} {2}".format(str(found), self.vpc_options.vpc_id, message),'OKBLUE')

        except Exception as e:
            message = "Can't list MSK Clusters\nError {0}".format(str(e))
            exit_critical(message)