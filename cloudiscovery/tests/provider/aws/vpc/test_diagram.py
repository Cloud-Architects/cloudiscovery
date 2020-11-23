from unittest import TestCase

from assertpy import assert_that

from provider.aws.vpc.diagram import (
    VpcDiagram,
    PUBLIC_SUBNET,
    PRIVATE_SUBNET,
    ASG_EC2_AGGREGATE_PREFIX,
    ASG_ECS_INSTANCE_AGGREGATE_PREFIX,
)
from shared.common import Resource, ResourceDigest, ResourceEdge


class TestVpcDiagram(TestCase):
    def test_public_subnet(self):
        sut = VpcDiagram("4")
        subnet_1_digest = ResourceDigest(id="1", type="aws_subnet")
        subnet_2_digest = ResourceDigest(id="2", type="aws_subnet")
        route_digest = ResourceDigest(id="3", type="aws_route_table")
        vpc_digest = ResourceDigest(id="4", type="aws_vpc")
        ec2_1_digest = ResourceDigest(id="5", type="aws_instance")
        ec2_2_digest = ResourceDigest(id="6", type="aws_instance")
        lambda_digest = ResourceDigest(id="6", type="aws_lambda_function")

        relations = [
            ResourceEdge(from_node=subnet_1_digest, to_node=vpc_digest),
            ResourceEdge(from_node=subnet_2_digest, to_node=vpc_digest),
            ResourceEdge(from_node=route_digest, to_node=vpc_digest),
            ResourceEdge(from_node=ec2_1_digest, to_node=subnet_1_digest),
            ResourceEdge(from_node=ec2_2_digest, to_node=subnet_2_digest),
            ResourceEdge(from_node=lambda_digest, to_node=subnet_1_digest),
            ResourceEdge(from_node=lambda_digest, to_node=subnet_2_digest),
        ]
        result = sut.group_by_group(
            [
                Resource(digest=subnet_1_digest, name=""),
                Resource(digest=subnet_2_digest, name=""),
                Resource(
                    digest=route_digest, name="", details="default: True, public: True"
                ),
                Resource(digest=vpc_digest, name=""),
                Resource(digest=ec2_1_digest, name=""),
                Resource(digest=ec2_2_digest, name=""),
                Resource(digest=lambda_digest, name=""),
            ],
            relations,
        )

        assert_that(result).contains_key("")
        assert_that(result[""]).is_length(6)
        for resource in result[""]:
            assert_that(resource.digest).is_not_equal_to(subnet_1_digest)
            assert_that(resource.digest).is_not_equal_to(subnet_2_digest)

        relationships = sut.process_relationships(result, relations)
        assert_that(relationships).is_length(8)
        assert_that(relationships).contains(
            ResourceEdge(
                from_node=ResourceDigest(id=PUBLIC_SUBNET, type="aws_subnet"),
                to_node=vpc_digest,
            )
        )
        assert_that(relationships).contains(
            ResourceEdge(from_node=route_digest, to_node=vpc_digest)
        )
        assert_that(relationships).contains(
            ResourceEdge(
                from_node=ec2_1_digest,
                to_node=ResourceDigest(id=PUBLIC_SUBNET, type="aws_subnet"),
            )
        )
        assert_that(relationships).contains(
            ResourceEdge(
                from_node=ec2_2_digest,
                to_node=ResourceDigest(id=PUBLIC_SUBNET, type="aws_subnet"),
            )
        )

    def test_private_subnet(self):
        sut = VpcDiagram("3")
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
                    digest=route_digest, name="", details="default: True, public: False"
                ),
                Resource(digest=vpc_digest, name=""),
                Resource(digest=ec2_digest, name=""),
            ],
            relations,
        )

        assert_that(result).contains_key("")
        assert_that(result[""]).is_length(4)
        for resource in result[""]:
            assert_that(resource.digest).is_not_equal_to(subnet_digest)

        relationships = sut.process_relationships(result, relations)
        assert_that(relationships).is_length(4)
        assert_that(relationships).contains(
            ResourceEdge(
                from_node=ResourceDigest(id=PRIVATE_SUBNET, type="aws_subnet"),
                to_node=vpc_digest,
            )
        )
        assert_that(relationships).contains(
            ResourceEdge(from_node=route_digest, to_node=vpc_digest)
        )
        assert_that(relationships).contains(
            ResourceEdge(
                from_node=ec2_digest,
                to_node=ResourceDigest(id=PRIVATE_SUBNET, type="aws_subnet"),
            )
        )

    def test_should_detect_public_and_private_subnet(self):
        sut = VpcDiagram("6")
        public_subnet_digest = ResourceDigest(id="1", type="aws_subnet")
        private_subnet_digest = ResourceDigest(id="2", type="aws_subnet")
        main_route_digest = ResourceDigest(id="3", type="aws_route_table")
        public_route_digest = ResourceDigest(id="4", type="aws_route_table")
        private_route_digest = ResourceDigest(id="5", type="aws_route_table")
        vpc_digest = ResourceDigest(id="6", type="aws_vpc")
        ec2_digest = ResourceDigest(id="7", type="aws_instance")

        relations = [
            ResourceEdge(from_node=public_subnet_digest, to_node=vpc_digest),
            ResourceEdge(from_node=private_subnet_digest, to_node=vpc_digest),
            ResourceEdge(from_node=main_route_digest, to_node=vpc_digest),
            ResourceEdge(from_node=public_route_digest, to_node=public_subnet_digest),
            ResourceEdge(from_node=private_route_digest, to_node=private_subnet_digest),
            ResourceEdge(from_node=ec2_digest, to_node=private_subnet_digest),
        ]
        result = sut.group_by_group(
            [
                Resource(digest=public_subnet_digest, name=""),
                Resource(digest=private_subnet_digest, name=""),
                Resource(
                    digest=main_route_digest,
                    name="",
                    details="default: True, public: False",
                ),
                Resource(
                    digest=public_route_digest,
                    name="",
                    details="default: False, public: True",
                ),
                Resource(
                    digest=private_route_digest,
                    name="",
                    details="default: False, public: False",
                ),
                Resource(digest=vpc_digest, name=""),
                Resource(digest=ec2_digest, name=""),
            ],
            relations,
        )

        assert_that(result).contains_key("")
        assert_that(result[""]).is_length(7)
        for resource in result[""]:
            assert_that(resource.digest).is_not_equal_to(public_subnet_digest)
            assert_that(resource.digest).is_not_equal_to(private_subnet_digest)

        relationships = sut.process_relationships(result, relations)
        assert_that(relationships).contains(
            ResourceEdge(
                from_node=public_route_digest,
                to_node=ResourceDigest(id=PUBLIC_SUBNET, type="aws_subnet"),
            )
        )
        assert_that(relationships).contains(
            ResourceEdge(
                from_node=private_route_digest,
                to_node=ResourceDigest(id=PRIVATE_SUBNET, type="aws_subnet"),
            )
        )
        assert_that(relationships).contains(
            ResourceEdge(
                from_node=ec2_digest,
                to_node=ResourceDigest(id=PRIVATE_SUBNET, type="aws_subnet"),
            )
        )

    def test_asg_ecs(self):
        sut = VpcDiagram("4")
        subnet_1_digest = ResourceDigest(id="1", type="aws_subnet")
        subnet_2_digest = ResourceDigest(id="2", type="aws_subnet")
        route_digest = ResourceDigest(id="3", type="aws_route_table")
        vpc_digest = ResourceDigest(id="4", type="aws_vpc")
        ec2_1_digest = ResourceDigest(id="5", type="aws_instance")
        ec2_2_digest = ResourceDigest(id="6", type="aws_instance")
        autoscaling_group_digest = ResourceDigest(
            id="asg_1", type="aws_autoscaling_group"
        )
        ecs_cluster_1_digest = ResourceDigest(id="8", type="aws_ecs_cluster")
        ecs_cluster_2_digest = ResourceDigest(id="9", type="aws_ecs_cluster")

        relations = [
            ResourceEdge(from_node=subnet_1_digest, to_node=vpc_digest),
            ResourceEdge(from_node=subnet_2_digest, to_node=vpc_digest),
            ResourceEdge(from_node=route_digest, to_node=vpc_digest),
            ResourceEdge(from_node=ec2_1_digest, to_node=subnet_1_digest),
            ResourceEdge(from_node=ec2_2_digest, to_node=subnet_2_digest),
            ResourceEdge(from_node=ec2_1_digest, to_node=autoscaling_group_digest),
            ResourceEdge(from_node=ec2_2_digest, to_node=autoscaling_group_digest),
            ResourceEdge(from_node=ecs_cluster_1_digest, to_node=ec2_1_digest),
            ResourceEdge(from_node=ecs_cluster_2_digest, to_node=ec2_2_digest),
        ]
        result = sut.group_by_group(
            [
                Resource(digest=subnet_1_digest, name=""),
                Resource(digest=subnet_2_digest, name=""),
                Resource(
                    digest=route_digest, name="", details="default: True, public: True"
                ),
                Resource(digest=vpc_digest, name=""),
                Resource(digest=ec2_1_digest, name=""),
                Resource(digest=ec2_2_digest, name=""),
                Resource(digest=ecs_cluster_1_digest, name=""),
                Resource(digest=ecs_cluster_2_digest, name=""),
                Resource(digest=autoscaling_group_digest, name=""),
            ],
            relations,
        )

        assert_that(result).contains_key("")
        assert_that(result[""]).is_length(6)
        for resource in result[""]:
            assert_that(resource.digest).is_not_equal_to(ec2_1_digest)
            assert_that(resource.digest).is_not_equal_to(ec2_2_digest)
            assert_that(resource.digest).is_not_equal_to(ecs_cluster_1_digest)
            assert_that(resource.digest).is_not_equal_to(ecs_cluster_2_digest)

        relationships = sut.process_relationships(result, relations)
        assert_that(relationships).contains(
            ResourceEdge(
                from_node=ResourceDigest(
                    id=ASG_ECS_INSTANCE_AGGREGATE_PREFIX + "asg_1",
                    type="aws_ecs_cluster",
                ),
                to_node=ResourceDigest(
                    id=ASG_EC2_AGGREGATE_PREFIX + "asg_1", type="aws_instance"
                ),
            )
        )
        assert_that(relationships).contains(
            ResourceEdge(
                from_node=ResourceDigest(
                    id=ASG_EC2_AGGREGATE_PREFIX + "asg_1", type="aws_instance"
                ),
                to_node=ResourceDigest(id=PUBLIC_SUBNET, type="aws_subnet"),
            )
        )
