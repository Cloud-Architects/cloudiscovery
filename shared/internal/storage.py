from concurrent.futures.thread import ThreadPoolExecutor
from shared.error_handler import exception
from shared.common import *
import json

class EFS(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    @exception
    def run(self):

        client = self.vpc_options.client('efs')
        
        """ get filesystems available """
        response = client.describe_file_systems()

        message_handler("\nChecking EFS MOUNT TARGETS...", "HEADER")

        if len(response["FileSystems"]) == 0:
            message_handler("Found 0 EFS File Systems in region {0}".format(self.vpc_options.region_name), "OKBLUE")
        else:
            found = 0
            message = ""

            """ iterate filesystems to get mount targets """
            for data in response["FileSystems"]:
                
                filesystem = client.describe_mount_targets(FileSystemId=data["FileSystemId"])

                """ iterate filesystems to get mount targets """
                for datafilesystem in filesystem['MountTargets']:

                    """ describe subnet to get VpcId """
                    ec2 = self.vpc_options.client('ec2')
                    
                    subnets = ec2.describe_subnets(SubnetIds=[datafilesystem['SubnetId']])

                    if subnets['Subnets'][0]['VpcId'] == self.vpc_options.vpc_id:
                        found += 1
                        message = message + "\nFileSystemId: {0} - NumberOfMountTargets: {1} - VpcId: {2}".format(
                            data['FileSystemId'], 
                            data['NumberOfMountTargets'], 
                            subnets['Subnets'][0]['VpcId']
                        )

            message_handler("Found {0} EFS Mount Target using VPC {1} {2}".format(str(found), self.vpc_options.vpc_id, message),'OKBLUE')

        return True

class S3POLICY(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    @exception
    def run(self):

        client = self.vpc_options.client('s3')
        
        """ get buckets available """
        response = client.list_buckets()

        message_handler("\nChecking S3 BUCKET POLICY...", "HEADER")

        if len(response["Buckets"]) == 0:
            message_handler("Found 0 S3 Buckets", "OKBLUE")
        else:
            found = 0
            message = ""

            """ iterate buckets to get policy """
            with ThreadPoolExecutor(15) as executor:
                results = executor.map(lambda data: self.analyze_bucket(client, data), response['Buckets'])
            for result in results:
                if result[0] is True:
                    found += 1
                    message += result[1]
            message_handler("Found {0} S3 Bucket Policy using VPC {1} {2}".format(str(found), self.vpc_options.vpc_id, message),'OKBLUE')

        return True

    def analyze_bucket(self, client, data):
        try:
            documentpolicy = client.get_bucket_policy(Bucket=data["Name"])

            document = json.dumps(documentpolicy, default=datetime_to_string)

            """ check either vpc_id or potencial subnet ip are found """
            ipvpc_found = check_ipvpc_inpolicy(document=document, vpc_options=self.vpc_options)

            if ipvpc_found is True:
                return True, "\nBucketName: {0} - {1}".format(
                    data['Name'],
                    self.vpc_options.vpc_id
                )
        except:
            pass
        return False, None
