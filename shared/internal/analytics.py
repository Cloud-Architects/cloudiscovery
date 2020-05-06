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

                    """ elasticsearch uses accesspolicies too, so check both situation """
                    if elasticsearch_domain['DomainStatus']['VPCOptions']['VPCId'] == self.vpc_options.vpc_id \
                    or self.vpc_options.vpc_id in document:
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