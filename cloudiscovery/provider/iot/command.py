from provider.iot.diagram import IoTDiagram
from shared.command import CommandRunner, BaseCommand
from shared.common import BaseAwsOptions, ResourceDigest
from shared.diagram import NoDiagram, BaseDiagram


class IotOptions(BaseAwsOptions):
    thing_name: str

    def __new__(cls, session, region_name, thing_name):
        """
        Iot options

        :param session:
        :param region_name:
        :param thing_name:
        """
        self = super(BaseAwsOptions, cls).__new__(cls, (session, region_name))
        self.thing_name = thing_name
        return self

    def iot_digest(self):
        return ResourceDigest(id=self.thing_name, type="aws_iot")


class Iot(BaseCommand):
    # pylint: disable=too-many-arguments
    def __init__(self, thing_name, region_names, session, diagram, filters):
        """
        Iot command

        :param thing_name:
        :param region_names:
        :param session:
        :param diagram:
        :param filters:
        """
        super().__init__(region_names, session, diagram, filters)
        self.thing_name = thing_name

    def run(self):
        command_runner = CommandRunner(self.filters)

        for region_name in self.region_names:

            # if thing_name is none, get all things and check
            if self.thing_name is None:
                client = self.session.client("iot", region_name=region_name)
                things = client.list_things()
                thing_options = IotOptions(
                    session=self.session, region_name=region_name, thing_name=things
                )
                diagram_builder: BaseDiagram
                if self.diagram:
                    diagram_builder = IoTDiagram(thing_name="")
                else:
                    diagram_builder = NoDiagram()
                command_runner.run(
                    provider="iot",
                    options=thing_options,
                    diagram_builder=diagram_builder,
                    title="AWS IoT Resources - Region {}".format(region_name),
                    filename=thing_options.resulting_file_name("iot"),
                )
            else:
                things = dict()
                things["things"] = [{"thingName": self.thing_name}]
                thing_options = IotOptions(
                    session=self.session, region_name=region_name, thing_name=things
                )

                if self.diagram:
                    diagram_builder = IoTDiagram(thing_name=self.thing_name)
                else:
                    diagram_builder = NoDiagram()

                command_runner.run(
                    provider="iot",
                    options=thing_options,
                    diagram_builder=diagram_builder,
                    title="AWS IoT {} Resources - Region {}".format(
                        self.thing_name, region_name
                    ),
                    filename=thing_options.resulting_file_name(
                        self.thing_name + "_iot"
                    ),
                )
