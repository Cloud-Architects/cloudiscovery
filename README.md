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
- MEDIA CONNECT
- MEDIA LIVE
- MEDIA STORE POLICY

### News

- Performs checks using thread concurrency
- Best information provided
- Integration with [Diagram](https://github.com/mingrammer/diagrams)
- Now this tool can check all VPCS in the same regions
- Support to Docker container

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

- The configured credentials must be associated to a user or role with proper permissions to do all checks. If you want to use a role with narrowed set of permissions just to perform network discovery, use a role from the following CF template shown below. To further increase security, you can add a block to check `aws:MultiFactorAuthPresent` condition in `AssumeRolePolicyDocument`. More on using IAM roles in the [configuration file](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-role.html).

```json
{
  "AWSTemplateFormatVersion": "2010-09-09",
  "Description": "Setups a role for diagram builder for all resources within an account",
  "Resources": {
    "NetworkDiscoveryRole": {
      "Type": "AWS::IAM::Role",
      "Properties": {
        "AssumeRolePolicyDocument" : {
          "Statement" : [
            {
              "Effect" : "Allow",
              "Principal" : {
                "AWS": { "Fn::Join" : [ "", [
                  "arn:aws:iam::", { "Ref" : "AWS::AccountId" }, ":root"
                ]]}
              },
              "Action" : [ "sts:AssumeRole" ]
            }
          ]
        },
        "Policies": [{
          "PolicyName": "additional-permissions",
          "PolicyDocument": {
            "Version": "2012-10-17",
            "Statement" : [
              {
                "Effect" : "Allow",
                "Action" : [
                  "kafka:ListClusters",
                  "synthetics:DescribeCanaries",
                  "medialive:ListInputs"
                ],
                "Resource": [ "*" ]
              }
            ]
          }
        }],
        "Path" : "/",
        "ManagedPolicyArns" : [
          "arn:aws:iam::aws:policy/job-function/ViewOnlyAccess",
          "arn:aws:iam::aws:policy/SecurityAudit"
        ]
      }
    }
  },
  "Outputs" : {
    "NetworkDiscoveryRoleArn" : {
      "Value" : { "Fn::GetAtt": [ "NetworkDiscoveryRole", "Arn" ]}
    }
  }
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

### Using a Docker container

To build docker container using Dockerfile

```sh
$ docker build -t aws-discovery-network .
```

After build container, you must start container using follow command. The run command will mount a filesystem with your actual aws cli credentials, then you won't need configure aws cli again.

```sh
$ docker run \
-it \
--mount type=bind,source=$HOME/.aws/,target=/root/.aws/,readonly \
aws-discovery-network \
/bin/bash

```

- If you are using Diagram output and due to fact container is a slim image of Python image, you must run aws-network-discovery.py with "--diagram False", otherwise you'll have an error about "xdg-open". The output file will be saved in "assets/diagrams".

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