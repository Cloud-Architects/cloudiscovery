from shared.diagram import BaseDiagram


class IoTDiagram(BaseDiagram):

    def __init__(self, name: str, filename: str, thing_name: str):
        super().__init__(name, filename)
        self.thing_name = thing_name
