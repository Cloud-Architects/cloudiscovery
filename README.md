# AWS Network Discovery

![python version](https://img.shields.io/badge/python-3.6%2C3.7%2C3.8-blue?logo=python)
[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://travis-ci.org/joemccann/dillinger)

AWS Network Discovery helps you analyze what's resources are using a custom VPC.

### Features

Following services are integrated

- EC2
- IAM POLICY
- Lambda
- RDS
- EFS 
- ELASTICACHE
- S3 POLICY
- ELASTICSEARCH
- DOCUMENTDB
- SQS QUEUE POLICY
- MSK
- NAT GATEWAY
- INTERNET GATEWAY (IGW)
- CLASSIC/NETWORK/APPLICATION LOAD BALANCING
- ROUTE TABLE
- SUBNET
- NACL
- SECURITY GROUP
- VPC PEERING
- VPC ENDPOINT
- EKS
- SYNTHETIC CANARIES
- EMR 
- ECS
- AUTOSCALING

### News

- Performs checks using thread concurrency
- Best information provided
- Integration with [Diagram](https://github.com/mingrammer/diagrams)
- Now this tool can check all VPCS in the same regions

### Requirements and Installation

This script has been written in python3+ using AWS-CLI and it works in Linux, Windows and OSX.

- Make sure the latest version of AWS-CLI is installed on your workstation, and other components needed, with Python pip already installed:

```sh
$ pip install -r requirements.txt
```

- Make sure you have properly configured your AWS-CLI with a valid Access Key and Region:

```sh
$ aws configure
```

- Those credentials must be associated to a user or role with proper permissions to do all checks. To make sure, add the AWS managed policies ViewOnlyAccess and SecurityAudit, to the user or role being used. Policies ARN are:

```sh
arn:aws:iam::aws:policy/job-function/ViewOnlyAccess
arn:aws:iam::aws:policy/SecurityAudit
```

- Due to fact AWS has not updated these policies to include Kafka Cluster and Synthetics Canaries read/list permissions, you must create a new policy with permissions bellow and attach to user.

```sh
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "kafka:ListClusters",
                "synthetics:DescribeCanaries"
            ],
            "Effect": "Allow",
            "Resource": "*"
        }
    ]
}
```

- (Optional) If you want to be able to switch between multiple AWS credentials and settings, you can configure [named profiles](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-profiles.html) and later pass profile name when running the tool.

### Usage

1. Run the aws-network-discovery command with follow options (if a region not informed, this script will try to get from ~/.aws/credentials):

```sh
$ ./aws-network-discovery.py [--vpc-id vpc-xxxxxxx] --region-name xx-xxxx-xxx [--profile-name profile] [--diagram True/False]
```

2. For help use:

```sh
$ ./aws-network-discovery.py -h
```

### Translate

This project support English and Portuguese (Brazil) languages. To contribute with a translation, follow this steps:

- Create a folder inside locales folder with prefix of new idiom with appropiate locale code (https://docs.oracle.com/cd/E23824_01/html/E26033/glset.html). Copy "locales/messages.pot" to locales/newfolder/LC_MESSAGES/.

- To build ".mo" file running this command from project root folder:

```sh
$ python msgfmt.py -o locales/NEWFOLDER/LC_MESSAGES/messages.mo locales/NEWFOLDER/LC_MESSAGES/messages
```

### TODO

- Improve documentation and code comments
- More services that uses VPC (I'll try add one a week)

### Contributing

If you have improvements or fixes, we would love to have your contributions. 