from unittest import TestCase

from provider.vpc.diagram import VpcDiagram, PUBLIC_SUBNET, PRIVATE_SUBNET
from shared.common import Resource, ResourceDigest, ResourceEdge
from shared.diagram import DIAGRAM_CLUSTER


class TestVpcDiagram(TestCase):
    def test_public_subnet(self):
        sut = VpcDiagram("name", "filename", "3")
        subnet_digest = ResourceDigest(id="1", type="aws_subnet")
        route_digest = ResourceDigest(id="2", type="aws_route_table")
        vpc_digest = ResourceDigest(id="3", type="aws_vpc")
        ec2_digest = ResourceDigest(id="4", type="aws_instance")

        relations = [
            ResourceEdge(from_node=subnet_digest, to_node=vpc_digest),
            ResourceEdge(from_node=route_digest, to_node=vpc_digest),
            ResourceEdge(from_node=ec2_digest, to_node=subnet_digest),
        ]
        result = sut.group_by_group(
            [
                Resource(digest=subnet_digest, name=""),
                Resource(
                    digest=route_digest, name="", details="default: True, public: True"
                ),
                Resource(digest=vpc_digest, name=""),
                Resource(digest=ec2_digest, name=""),
            ],
            relations,
        )

        self.assertTrue("" in result)
        self.assertTrue(len(result[""]) == 3)
        self.assertTrue(PUBLIC_SUBNET in result)
        self.assertTrue(len(result[PUBLIC_SUBNET]) == 1)
        self.assertTrue(result[PUBLIC_SUBNET][0].digest == subnet_digest)
        self.assertTrue(PRIVATE_SUBNET not in result)

        relationships = sut.process_relationships(result, relations)
        self.assertIn(
            ResourceEdge(from_node=subnet_digest, to_node=vpc_digest), relationships
        )
        self.assertIn(
            ResourceEdge(from_node=route_digest, to_node=vpc_digest), relationships
        )
        self.assertIn(
            ResourceEdge(
                from_node=ec2_digest,
                to_node=ResourceDigest(id=PUBLIC_SUBNET, type=DIAGRAM_CLUSTER),
            ),
            relationships,
        )

        self.assertTrue("" in result)


def test_group_by_group_should_detect_private_subnet(self):
    pass


def test_process_relationships_should_detect_private_subnet(self):
    pass


def test_group_by_group_should_detect_public_and_private_subnet(self):
    pass


def test_process_relationships_should_detect_public_and_public_subnet(self):
    pass
