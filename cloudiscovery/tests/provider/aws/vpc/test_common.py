from unittest import TestCase
from unittest.mock import MagicMock

from provider.aws.vpc.command import check_ipvpc_inpolicy


class Test(TestCase):
    def test_check_ipvpc_inpolicy(self):
        vpce = {"VpcEndpoints": [{"VpcEndpointId": "vpce-1234abcd", "VpcId": "dummy"}]}
        policy = """
        {"Version":"2012-10-17","Id":"arn:queue","Statement":
        [{"Effect":"Allow","Principal":"*","Action":"SQS:*","Resource":"arn:queue"},
        {"Effect":"Allow","Principal":"*","Action":"sqs:*","Resource":"arn:queue","Condition":
        {"StringEquals":{"aws:sourceVpce":"vpce-1234abcd"}}}]}
        """
        vpc_options = MagicMock()
        vpc_options.vpc_id = "dummy"
        vpc_options.client.return_value.describe_vpc_endpoints.return_value = vpce
        result = check_ipvpc_inpolicy(policy, vpc_options)
        self.assertTrue("vpce-1234abcd" in result)

    def test_check_vpce_inpolicy(self):
        subnets = {
            "Subnets": [
                {
                    "CidrBlock": "10.0.64.0/18",
                    "SubnetId": "subnet-123",
                    "VpcId": "dummy",
                }
            ]
        }
        policy = """
        {"Version":"2012-10-17","Id":"arn:queue","Statement":
        [{"Effect":"Allow","Principal":"*","Action":"SQS:*","Resource":"arn:queue"},
        {"Effect":"Allow","Principal":"*","Action":"sqs:*","Resource":"arn:queue","Condition":
        {"StringEquals":{"aws:sourceIp": "10.0.0.0/16"}}}]}
        """
        vpc_options = MagicMock()
        vpc_options.vpc_id = "dummy"
        vpc_options.client.return_value.describe_subnets.return_value = subnets
        result = check_ipvpc_inpolicy(policy, vpc_options)
        self.assertTrue("10.0.0.0/16" in result)
        self.assertTrue("10.0.64.0/18" in result)
        self.assertTrue("subnet-123" in result)
