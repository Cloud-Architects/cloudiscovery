# AWS Network Discovery

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

### Usage

1. Run the aws-network-discovery command with follow options (if a region not informed, this script will try to get from ~/.aws/credentials):

```sh
$ ./aws-network-discovery.py --vpc-id vpc-xxxxxxx --region-name xx-xxxx-xxx
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
- Custom logging control and reporting improvement.

### License

Copyright 2020 Conversando Na Nuvem (https://www.youtube.com/channel/UCuI2nDGLq_yjY9JNsDYStMQ/) - Leandro Damascena

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
following disclaimer in the documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote
products derived from this software without specific prior written permission.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

