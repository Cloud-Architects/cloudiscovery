from typing import List

from shared.common import (
    Resource,
    ResourceEdge,
    Filterable,
    ResourceTag,
    ResourceType,
)


def filter_resources(
    resources: List[Resource], filters: List[Filterable]
) -> List[Resource]:
    if not filters:
        return resources

    filtered_resources = []
    for resource in resources:
        matches_filter = False
        for resource_filter in filters:
            if isinstance(resource_filter, ResourceTag):
                for resource_tag in resource.tags:
                    if (
                        resource_tag.key == resource_filter.key
                        and resource_tag.value == resource_filter.value
                    ):
                        matches_filter = True
            elif isinstance(resource_filter, ResourceType):
                if resource.digest.type == resource_filter.type:
                    matches_filter = True
        if matches_filter:
            filtered_resources.append(resource)
    return filtered_resources


def filter_relations(
    filtered_resources: List[Resource], resource_relations: List[ResourceEdge]
):
    filtered_relations: List[ResourceEdge] = []

    for resource_relation in resource_relations:
        is_from_present = False
        is_to_present = False
        for resource in filtered_resources:
            if resource_relation.from_node == resource.digest:
                is_from_present = True
            if resource_relation.to_node == resource.digest:
                is_to_present = True
        if is_from_present and is_to_present:
            filtered_relations.append(resource_relation)
    return filtered_relations


def execute_provider(options, data) -> (List[Resource], List[ResourceEdge]):
    provider_instance = data[1](options)
    provider_resources = provider_instance.get_resources()
    provider_resource_relations = provider_instance.get_relations()
    return provider_resources, provider_resource_relations
