from provider.iot.diagram import IoTDiagram
from shared.command import CommandRunner, BaseCommand
from shared.common import *
from shared.diagram import NoDiagram, BaseDiagram

class IotOptions(BaseOptions):
    thing_name: str

    def __new__(cls, session, region_name, thing_name):
        self = super(BaseOptions, cls).__new__(cls, (session, region_name))
        self.thing_name = thing_name
        return self

    def iot_digest(self):
        return ResourceDigest(id=self.thing_name,
                              type='aws_iot')

class Iot(BaseCommand):
    def __init__(self, thing_name, region_name, session, diagram):
        super().__init__(region_name, session, diagram)
        self.thing_name = thing_name

    def run(self):
        self.check_region()

        command_runner = CommandRunner()

        regions = self.region_name

        for region in regions:

            self.region_name = region["RegionName"]

            """ if thing_name is none, get all things and check """
            if self.thing_name is None:
                client = self.session.client('iot', region_name=self.region_name)
                things = client.list_things()
                thing_options = IotOptions(session=self.session, region_name=self.region_name, thing_name=things)
                diagram_builder: BaseDiagram
                if self.diagram:
                    diagram_builder = IoTDiagram(name="AWS IoT Resources - Region {}".format(self.region_name),
                                                filename=self.region_name,
                                                thing_name=None)
                else:
                    diagram_builder = NoDiagram()
                command_runner.run("iot", thing_options, diagram_builder)
            else:
                things = dict()
                things['things'] = [{'thingName': self.thing_name}] 
                thing_options = IotOptions(session=self.session, region_name=self.region_name, thing_name=things)

                if self.diagram:
                    diagram_builder = IoTDiagram(name="AWS IoT {} Resources - Region {}".format(self.thing_name, self.region_name),
                                                filename=self.thing_name,
                                                thing_name=self.thing_name)
                else:
                    diagram_builder = NoDiagram()

                command_runner.run("iot", thing_options, diagram_builder)