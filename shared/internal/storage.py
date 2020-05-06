from shared.common import *
import json

class EFS(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    def run(self):
        try:
            client = self.vpc_options.session.client('efs', region_name=self.vpc_options.region_name)
            
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
                        ec2 = self.vpc_options.session.client('ec2', region_name=self.vpc_options.region_name)
                        
                        subnets = ec2.describe_subnets(SubnetIds=[datafilesystem['SubnetId']])

                        if subnets['Subnets'][0]['VpcId'] == self.vpc_options.vpc_id:
                            found += 1
                            message = message + "\nFileSystemId: {0} - NumberOfMountTargets: {1} - VpcId: {2}".format(
                                data['FileSystemId'], 
                                data['NumberOfMountTargets'], 
                                subnets['Subnets'][0]['VpcId']
                            )

                message_handler("Found {0} EFS Mount Target using VPC {1} {2}".format(str(found), self.vpc_options.vpc_id, message),'OKBLUE')
        except Exception as e:
            message = "Can't list EFS MOUNT TARGETS\nError {0}".format(str(e))
            exit_critical(message)

class S3POLICY(object):
    
    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    def run(self):
        try:
            client = self.vpc_options.session.client('s3', region_name=self.vpc_options.region_name)
            
            """ get buckets available """
            response = client.list_buckets()

            message_handler("\nChecking S3 BUCKET POLICY...", "HEADER")

            if len(response["Buckets"]) == 0:
                message_handler("Found 0 S3 Bucket", "OKBLUE")
            else:
                found = 0
                message = ""

                """ iterate buckets to get policy """
                for data in response['Buckets']:
                    
                    #documentpolicy = client.get_bucket_policy(Bucket=data["Name"])
                    try:
                        documentpolicy = client.get_bucket_policy(Bucket=data["Name"])

                        document = json.dumps(documentpolicy, default=datetime_to_string) 

                        if self.vpc_options.vpc_id in document:
                            found += 1
                            message = message + "\nBucketName: {0} - {1}".format(
                                data['Name'],
                                self.vpc_options.vpc_id
                            )
                    except:
                        pass

                message_handler("Found {0} S3 Bucket Policy using VPC {1} {2}".format(str(found), self.vpc_options.vpc_id, message),'OKBLUE')
        
        except Exception as e:
            message = "Can't list S3 BUCKETS\nError {0}".format(str(e))
            exit_critical(message)