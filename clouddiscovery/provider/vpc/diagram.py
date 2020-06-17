from typing import List, Dict, Optional

from shared.common import ResourceEdge, Resource, ResourceDigest
from shared.diagram import BaseDiagram, add_resource_to_group

PUBLIC_SUBNET = "{public subnet}"
PRIVATE_SUBNET = "{private subnet}"
ASG_EC2_AGGREGATE_PREFIX = "asg_ec2_aggregate_"
ASG_ECS_INSTANCE_AGGREGATE_PREFIX = "asg_ecs_instance_aggregate_"


def to_node_get_aggregated(
    resource_relation: ResourceEdge, resources: List[Resource]
) -> Optional[Resource]:
    for resource in resources:
        if (
            " subnet}" in resource.digest.id
            or ASG_EC2_AGGREGATE_PREFIX in resource.digest.id
            or ASG_ECS_INSTANCE_AGGREGATE_PREFIX in resource.digest.id
        ):
            if resource_relation.to_node.id in resource.details:
                return resource
    return None


def from_node_get_aggregated(
    resource_relation: ResourceEdge, resources: List[Resource]
) -> Optional[Resource]:
    for resource in resources:
        if (
            " subnet}" in resource.digest.id
            or ASG_EC2_AGGREGATE_PREFIX in resource.digest.id
            or ASG_ECS_INSTANCE_AGGREGATE_PREFIX in resource.digest.id
        ):
            if resource_relation.from_node.id in resource.details:
                return resource
    return None


def aggregate_subnets(groups, group_type, group_name):
    if group_type in groups:
        subnet_ids = []
        for subnet in groups[group_type]:
            subnet_ids.append(subnet.digest.id)
        groups[""].append(
            Resource(
                digest=ResourceDigest(id=group_type, type="aws_subnet"),
                name=group_name + ", ".join(subnet_ids),
                details=", ".join(subnet_ids),
            )
        )


def get_ec2_asg(
    initial_resource_relations: List[ResourceEdge], ec2_digest: Optional[ResourceDigest]
) -> Optional[str]:
    if ec2_digest is None:
        return None
    for relation in initial_resource_relations:
        if (
            relation.from_node == ec2_digest
            and relation.to_node.type == "aws_autoscaling_group"
        ):
            return relation.to_node.id
    return None


def get_ecs_ec2(
    initial_resource_relations: List[ResourceEdge], ecs_instance_digest: ResourceDigest
) -> Optional[ResourceDigest]:
    for relation in initial_resource_relations:
        if (
            relation.from_node == ecs_instance_digest
            and relation.to_node.type == "aws_instance"
        ):
            return relation.to_node
    return None


def aggregate_asg_groups(
    groups: Dict[str, List[Resource]], prefix: str, aggregate_name: str
):
    for group_name, group_elements in groups.items():
        if group_name.startswith(prefix):
            agg_type = "none"
            elem_ids = []
            for element in group_elements:
                agg_type = element.digest.type
                elem_ids.append(element.digest.id)
            agg_resource = Resource(
                digest=ResourceDigest(id=group_name, type=agg_type),
                name=aggregate_name + "({})".format(len(group_elements)),
                details=",".join(elem_ids),
            )
            add_resource_to_group(groups, "", agg_resource)


class VpcDiagram(BaseDiagram):
    def __init__(self, vpc_id: str):
        """
        VPC diagram

        :param vpc_id:
        """
        super().__init__(
            "sfdp"
        )  # Change to fdp and clusters once mingrammer/diagrams#17 is done
        self.vpc_id = vpc_id

    # pylint: disable=too-many-branches
    def group_by_group(
        self, resources: List[Resource], initial_resource_relations: List[ResourceEdge]
    ) -> Dict[str, List[Resource]]:
        groups: Dict[str, List[Resource]] = {"": []}
        # pylint: disable=too-many-nested-blocks
        for resource in resources:
            if resource.digest.type == "aws_subnet":
                associated_tables = []
                for relation in initial_resource_relations:
                    if relation.from_node.type == "aws_route_table" and (
                        relation.to_node == resource.digest
                        or (
                            relation.to_node.type == "aws_vpc"
                            and relation.to_node.id == self.vpc_id
                        )
                    ):
                        for resource_2 in resources:
                            if resource_2.digest == relation.from_node:
                                associated_tables.append(resource_2)
                is_public = False
                for associated_table in associated_tables:
                    if "public: True" in associated_table.details:
                        is_public = True
                if is_public:
                    add_resource_to_group(groups, PUBLIC_SUBNET, resource)
                else:
                    add_resource_to_group(groups, PRIVATE_SUBNET, resource)
            elif resource.digest.type == "aws_instance":
                related_asg = get_ec2_asg(initial_resource_relations, resource.digest)
                if related_asg is not None:
                    add_resource_to_group(
                        groups, ASG_EC2_AGGREGATE_PREFIX + related_asg, resource
                    )
                else:
                    add_resource_to_group(groups, "", resource)
            elif resource.digest.type == "aws_ecs_cluster":
                related_ec2 = get_ecs_ec2(initial_resource_relations, resource.digest)
                related_asg = get_ec2_asg(initial_resource_relations, related_ec2)
                if related_asg is not None:
                    add_resource_to_group(
                        groups,
                        ASG_ECS_INSTANCE_AGGREGATE_PREFIX + related_asg,
                        resource,
                    )
                else:
                    add_resource_to_group(groups, "", resource)
            else:
                add_resource_to_group(groups, "", resource)

        aggregate_asg_groups(groups, ASG_EC2_AGGREGATE_PREFIX, "EC2 instances for ASG ")
        aggregate_asg_groups(
            groups, ASG_ECS_INSTANCE_AGGREGATE_PREFIX, "EC2 instances for ECS cluster "
        )

        aggregate_subnets(groups, PUBLIC_SUBNET, "Public subnets: ")
        aggregate_subnets(groups, PRIVATE_SUBNET, "Private subnets: ")

        return {"": groups[""]}

    def process_relationships(
        self,
        grouped_resources: Dict[str, List[Resource]],
        resource_relations: List[ResourceEdge],
    ) -> List[ResourceEdge]:
        relations: List[ResourceEdge] = []
        for resource in grouped_resources[""]:
            if resource.digest.type == "aws_subnet":
                if (
                    resource.digest.id == PUBLIC_SUBNET
                    or resource.digest.id == PRIVATE_SUBNET
                ):
                    relations.append(
                        ResourceEdge(
                            from_node=resource.digest,
                            to_node=ResourceDigest(id=self.vpc_id, type="aws_vpc"),
                        )
                    )
            elif ASG_EC2_AGGREGATE_PREFIX in resource.digest.id:
                prefix_len = len(ASG_EC2_AGGREGATE_PREFIX)
                asg_name = resource.digest.id[prefix_len:]
                relations.append(
                    ResourceEdge(
                        from_node=ResourceDigest(
                            id=resource.digest.id, type="aws_instance"
                        ),
                        to_node=ResourceDigest(
                            id=asg_name, type="aws_autoscaling_group"
                        ),
                    )
                )
            elif ASG_ECS_INSTANCE_AGGREGATE_PREFIX in resource.digest.id:
                prefix_len = len(ASG_ECS_INSTANCE_AGGREGATE_PREFIX)
                asg_name = resource.digest.id[prefix_len:]
                relations.append(
                    ResourceEdge(
                        from_node=ResourceDigest(
                            id=resource.digest.id, type="aws_ecs_cluster"
                        ),
                        to_node=ResourceDigest(
                            id=asg_name, type="aws_autoscaling_group"
                        ),
                    )
                )
        for resource_relation in resource_relations:
            aggregate_digest_to_node = to_node_get_aggregated(
                resource_relation, grouped_resources[""]
            )
            aggregate_digest_from_node = from_node_get_aggregated(
                resource_relation, grouped_resources[""]
            )
            if aggregate_digest_to_node and aggregate_digest_from_node:
                relations.append(
                    ResourceEdge(
                        from_node=aggregate_digest_from_node.digest,
                        to_node=aggregate_digest_to_node.digest,
                    )
                )
            elif aggregate_digest_to_node:
                relations.append(
                    ResourceEdge(
                        from_node=resource_relation.from_node,
                        to_node=aggregate_digest_to_node.digest,
                    )
                )
            elif aggregate_digest_from_node:
                relations.append(
                    ResourceEdge(
                        from_node=aggregate_digest_from_node.digest,
                        to_node=resource_relation.to_node,
                    )
                )
            else:
                relations.append(resource_relation)

        return relations
