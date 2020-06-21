from typing import List, Dict

from shared.common import ResourceEdge, Resource, ResourceDigest
from shared.diagram import BaseDiagram, Mapsources, add_resource_to_group

ROLE_AGGREGATE_PREFIX = "aggregate_"


class PolicyDiagram(BaseDiagram):
    def __init__(self):
        """
        Policy diagram
        """
        super().__init__("fdp")

    # pylint: disable=too-many-locals,too-many-branches
    def group_by_group(
        self, resources: List[Resource], initial_resource_relations: List[ResourceEdge]
    ) -> Dict[str, List[Resource]]:
        ordered_resources: Dict[str, List[Resource]] = dict()
        for resource in resources:
            if Mapsources.mapresources.get(resource.digest.type) is not None:
                if resource.digest.type == "aws_iam_role":

                    got_policy = False
                    principals = {}
                    for rel in initial_resource_relations:
                        if (
                            rel.from_node == resource.digest
                            and rel.to_node.type == "aws_iam_policy"
                        ):
                            got_policy = True
                        if (
                            rel.from_node == resource.digest
                            and rel.label == "assumed by"
                        ):
                            principals[rel.to_node.id + "|" + rel.to_node.type] = True

                    if got_policy and len(principals) != 0:
                        add_resource_to_group(
                            ordered_resources, resource.group, resource
                        )
                    else:
                        for principal in principals:
                            add_resource_to_group(
                                ordered_resources, "to_agg_" + principal, resource
                            )
                else:
                    add_resource_to_group(ordered_resources, resource.group, resource)

        keys_to_remove = []
        for key, values in ordered_resources.items():
            if "to_agg_" in key:
                names = []
                for value in values:
                    names.append(value.digest.id)
                to_agg_len = len("to_agg_")
                principal_id_type = key[to_agg_len:]
                principal_id = principal_id_type.rsplit("|", 1)[0]
                principal_type = principal_id_type.rsplit("|", 1)[1]
                aggregate_digest = ResourceDigest(
                    id=ROLE_AGGREGATE_PREFIX + principal_id, type="aws_iam_role"
                )
                aggregate_role = Resource(
                    digest=aggregate_digest,
                    name="Roles for {} ({})".format(principal_id, len(values)),
                    details=",".join(names),
                )
                initial_resource_relations.append(
                    ResourceEdge(
                        from_node=aggregate_digest,
                        to_node=ResourceDigest(id=principal_id, type=principal_type),
                        label="assumed by",
                    )
                )
                add_resource_to_group(ordered_resources, "", aggregate_role)
                keys_to_remove.append(key)
        for key in keys_to_remove:
            ordered_resources.pop(key, None)

        return ordered_resources

    def process_relationships(
        self,
        grouped_resources: Dict[str, List[Resource]],
        resource_relations: List[ResourceEdge],
    ) -> List[ResourceEdge]:
        aggregated_roles = {}
        for resource in grouped_resources[""]:
            if (
                resource.digest.type == "aws_iam_role"
                and resource.digest.id.startswith(ROLE_AGGREGATE_PREFIX)
            ):
                for role in resource.details.split(","):
                    aggregated_roles[role] = resource.digest.id
        filtered_resources: List[ResourceEdge] = []
        for resource_relation in resource_relations:
            if resource_relation.from_node.id not in aggregated_roles:
                filtered_resources.append(resource_relation)

        return filtered_resources
