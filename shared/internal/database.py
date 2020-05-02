import boto3
from shared.common import * 

class RDS(object):
    
    def __init__(self, vpc_id, region_name):
        self.vpc_id = vpc_id
        self.region_name = region_name
    
    def run(self):
        try:
            client = boto3.client('rds', region_name=self.region_name)
            
            response = client.describe_db_instances()
            
            message_handler("\nChecking RDS INSTANCES...", "HEADER")

            if (len(response["DBInstances"]) == 0):
                message_handler("Found 0 RDS Instances in region {0}".format(self.region_name), "OKBLUE")
            else:
                found = 0
                message = ""
                for data in response["DBInstances"]:
                    if (data['DBSubnetGroup']['VpcId'] == self.vpc_id):
                        found += 1
                        message = message + "\nDBInstanceIdentifier: {0} - Engine: {1} - VpcId {2}".format(
                            data["DBInstanceIdentifier"], 
                            data["Engine"], 
                            data['DBSubnetGroup']['VpcId']
                        )
                message_handler("Found {0} RDS Instances using VPC {1} {2}".format(str(found), self.vpc_id, message),'OKBLUE')
                

        except Exception as e:
            message = "Can't list RDS Instances\nError {0}".format(str(e))
            exit_critical(message)

class ELASTICACHE(object):
    
    def __init__(self, vpc_id, region_name):
        self.vpc_id = vpc_id
        self.region_name = region_name
    
    def run(self):
        try:
            client = boto3.client('elasticache', region_name=self.region_name)
            
            """ get all cache clusters """
            response = client.describe_cache_clusters()
    
            message_handler("\nChecking ELASTICACHE CLUSTERS...", "HEADER")

            if (len(response['CacheClusters']) == 0):
                message_handler("Found 0 Elasticache Clusters in region {0}".format(self.region_name), "OKBLUE")
            else:
                found = 0
                message = ""

                """ iterate cache clusters to get subnet groups """
                for data in response['CacheClusters']:

                    cachesubnet = client.describe_cache_subnet_groups(CacheSubnetGroupName=data['CacheSubnetGroupName'])

                    if (cachesubnet['CacheSubnetGroups'][0]['VpcId'] == self.vpc_id):
                        found += 1
                        message = message + "\nCacheClusterId: {0} - CacheSubnetGroupName: {1} - Engine: {2} - VpcId: {3}".format(
                            data["CacheClusterId"],
                            data["CacheSubnetGroupName"], 
                            data["Engine"], 
                            cachesubnet['CacheSubnetGroups'][0]['VpcId']
                        )
                message_handler("Found {0} Elasticache Clusters using VPC {1} {2}".format(str(found), self.vpc_id, message),'OKBLUE')
                

        except Exception as e:
            message = "Can't list Elasticache Clusters\nError {0}".format(str(e))
            exit_critical(message)