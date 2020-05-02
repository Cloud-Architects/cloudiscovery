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