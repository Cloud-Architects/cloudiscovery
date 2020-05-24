from concurrent.futures.thread import ThreadPoolExecutor
from shared.error_handler import exception
from shared.common import *
import json
from typing import List

class EFS(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    @exception
    def run(self) -> List[Resource]:

        client = self.vpc_options.client('efs')

        resources_found = []
        
        """ get filesystems available """
        response = client.describe_file_systems()

        message_handler("Collecting data from EFS MOUNT TARGETS...", "HEADER")

        if len(response["FileSystems"]) > 0:

            """ iterate filesystems to get mount targets """
            for data in response["FileSystems"]:
                
                filesystem = client.describe_mount_targets(FileSystemId=data["FileSystemId"])

                """ iterate filesystems to get mount targets """
                for datafilesystem in filesystem['MountTargets']:

                    """ describe subnet to get VpcId """
                    ec2 = self.vpc_options.client('ec2')
                    
                    subnets = ec2.describe_subnets(SubnetIds=[datafilesystem['SubnetId']])

                    if subnets['Subnets'][0]['VpcId'] == self.vpc_options.vpc_id:

                        resources_found.append(Resource(id=data['FileSystemId'],
                                                        name=data['Name'],
                                                        type='aws_efs_file_system',
                                                        details=''))

        return resources_found

class S3POLICY(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    @exception
    def run(self) -> List[Resource]:

        client = self.vpc_options.client('s3')

        resources_found = []
        
        """ get buckets available """
        response = client.list_buckets()

        message_handler("Collecting data from S3 BUCKET POLICY...", "HEADER")

        if len(response["Buckets"]) > 0:

            """ iterate buckets to get policy """
            with ThreadPoolExecutor(15) as executor:
                results = executor.map(lambda data: self.analyze_bucket(client, data), response['Buckets'])

            for result in results:
                if result[0] is True:
                    resources_found.append(result[1])

        return resources_found

    def analyze_bucket(self, client, data):
        try:
            documentpolicy = client.get_bucket_policy(Bucket=data["Name"])

            document = json.dumps(documentpolicy, default=datetime_to_string)

            """ check either vpc_id or potencial subnet ip are found """
            ipvpc_found = check_ipvpc_inpolicy(document=document, vpc_options=self.vpc_options)

            if ipvpc_found is True:

                return True, Resource(id=data['Name'],
                                      name=data['Name'],
                                      type='aws_s3_bucket_policy',
                                      details='')
        except:
            pass
        return False, None
