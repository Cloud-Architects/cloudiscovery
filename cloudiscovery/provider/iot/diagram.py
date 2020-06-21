from shared.diagram import BaseDiagram


class IoTDiagram(BaseDiagram):
    def __init__(self, thing_name: str):
        """
        Iot diagram

        :param thing_name:
        """
        super().__init__()
        self.thing_name = thing_name
