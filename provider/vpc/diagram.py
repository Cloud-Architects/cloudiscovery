from typing import List, Dict, Optional

from shared.common import ResourceEdge, Resource, ResourceDigest
from shared.diagram import BaseDiagram, Mapsources

PUBLIC_SUBNET = "{public subnet}"
PRIVATE_SUBNET = "{private subnet}"


def to_node_get_aggregated(
    resource_relation: ResourceEdge, resources: List[Resource]
) -> Optional[Resource]:
    for resource in resources:
        if (
            " subnet}" in resource.digest.id
            and resource_relation.to_node.id in resource.name
        ):
            return resource
    return None


def aggregate_subnets(groups, group_type):
    if group_type in groups:
        subnet_ids = []
        for subnet in groups[group_type]:
            subnet_ids.append(subnet.digest.id)
        groups[""].append(
            Resource(
                digest=ResourceDigest(id=group_type, type="aws_subnet"),
                name=", ".join(subnet_ids),
            )
        )


class VpcDiagram(BaseDiagram):
    def __init__(self, name: str, filename: str, vpc_id: str):
        super().__init__(
            name, filename, "sfdp"
        )  # Change to fdp and clusters once mingrammer/diagrams#17 is done
        self.vpc_id = vpc_id

    def group_by_group(
        self, resources: List[Resource], initial_resource_relations: List[ResourceEdge]
    ) -> Dict[str, List[Resource]]:
        groups: Dict[str, List[Resource]] = {"": []}
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
                    if PUBLIC_SUBNET in groups:
                        groups[PUBLIC_SUBNET].append(resource)
                    else:
                        groups[PUBLIC_SUBNET] = [resource]
                else:
                    if PRIVATE_SUBNET in groups:
                        groups[PRIVATE_SUBNET].append(resource)
                    else:
                        groups[PRIVATE_SUBNET] = [resource]
            else:
                if Mapsources.mapresources.get(resource.digest.type) is not None:
                    groups[""].append(resource)

        aggregate_subnets(groups, PUBLIC_SUBNET)
        aggregate_subnets(groups, PRIVATE_SUBNET)

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
        for resource_relation in resource_relations:
            aggregated_subnet = to_node_get_aggregated(
                resource_relation, grouped_resources[""]
            )
            if aggregated_subnet:
                relations.append(
                    ResourceEdge(
                        from_node=resource_relation.from_node,
                        to_node=aggregated_subnet.digest,
                    )
                )
            else:
                relations.append(resource_relation)

        return relations
