from shared.diagram import BaseDiagram


class VpcDiagram(BaseDiagram):
    def __init__(self, name: str, filename: str, vpc_id: str):
        super().__init__(name, filename)
        self.vpc_id = vpc_id
