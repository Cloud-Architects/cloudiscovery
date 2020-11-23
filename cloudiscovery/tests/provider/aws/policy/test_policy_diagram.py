from unittest import TestCase

from assertpy import assert_that

from provider.aws.policy.diagram import PolicyDiagram, ROLE_AGGREGATE_PREFIX
from shared.common import Resource, ResourceDigest, ResourceEdge


class TestPolicyDiagram(TestCase):
    def test_role_aggregation(self):
        sut = PolicyDiagram()
        principal_digest = ResourceDigest(
            id="ecs.amazonaws.com", type="aws_ecs_cluster"
        )
        role_1_digest = ResourceDigest(id="AWSServiceRoleForECS1", type="aws_iam_role")
        role_2_digest = ResourceDigest(id="AWSServiceRoleForECS2", type="aws_iam_role")
        role_3_digest = ResourceDigest(id="AWSServiceRoleForECS3", type="aws_iam_role")
        policy_digest = ResourceDigest(
            id="arn:aws:iam::policy/service-role/AmazonEC2ContainerServiceforEC2Role",
            type="aws_iam_policy",
        )

        relations = [
            ResourceEdge(
                from_node=role_1_digest, to_node=principal_digest, label="assumed by"
            ),
            ResourceEdge(
                from_node=role_2_digest, to_node=principal_digest, label="assumed by"
            ),
            ResourceEdge(
                from_node=role_3_digest, to_node=principal_digest, label="assumed by"
            ),
            ResourceEdge(from_node=role_3_digest, to_node=policy_digest),
        ]
        result = sut.group_by_group(
            [
                Resource(digest=principal_digest, name="principal"),
                Resource(digest=role_1_digest, name=""),
                Resource(digest=role_2_digest, name=""),
                Resource(digest=role_3_digest, name=""),
                Resource(digest=policy_digest, name=""),
            ],
            relations,
        )

        assert_that(result).contains_key("")
        assert_that(result[""]).is_length(4)
        for resource in result[""]:
            assert_that(resource.digest).is_not_equal_to(role_1_digest)
            assert_that(resource.digest).is_not_equal_to(role_2_digest)

        relationships = sut.process_relationships(result, relations)
        assert_that(relationships).is_length(3)
        assert_that(relationships).contains(
            ResourceEdge(
                from_node=ResourceDigest(
                    id=ROLE_AGGREGATE_PREFIX + principal_digest.id, type="aws_iam_role"
                ),
                to_node=principal_digest,
                label="assumed by",
            )
        )
