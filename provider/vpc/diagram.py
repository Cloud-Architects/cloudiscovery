from typing import List, Dict

from shared.common import ResourceEdge, Resource
from shared.diagram import BaseDiagram


class VpcDiagram(BaseDiagram):
    def __init__(self, name: str, filename: str, vpc_id: str):
        super().__init__(name, filename)
        self.vpc_id = vpc_id

    def group_by_group(self, resources: List[Resource]) -> Dict[str, List[Resource]]:
        return super().group_by_group(resources)

    def process_relationships(
        self,
        grouped_resources: Dict[str, List[Resource]],
        resource_relations: List[ResourceEdge],
    ) -> List[ResourceEdge]:
        return super().process_relationships(resource_relations, resource_relations)
