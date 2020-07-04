from typing import List

from provider.iot.diagram import IoTDiagram
from shared.common import ResourceDigest, Filterable, BaseOptions
from shared.common_aws import BaseAwsOptions, BaseAwsCommand, AwsCommandRunner
from shared.diagram import NoDiagram, BaseDiagram


class IotOptions(BaseAwsOptions, BaseOptions):
    thing_name: str

    # pylint: disable=too-many-arguments
    def __init__(self, verbose, filters, session, region_name, thing_name):
        BaseAwsOptions.__init__(self, session, region_name)
        BaseOptions.__init__(self, verbose, filters)
        self.thing_name = thing_name

    def iot_digest(self):
        return ResourceDigest(id=self.thing_name, type="aws_iot")


class Iot(BaseAwsCommand):
    # pylint: disable=too-many-arguments
    def __init__(self, thing_name, region_names, session):
        """
        Iot command

        :param thing_name:
        :param region_names:
        :param session:
        """
        super().__init__(region_names, session)
        self.thing_name = thing_name

    def run(
        self,
        diagram: bool,
        verbose: bool,
        services: List[str],
        filters: List[Filterable],
    ):
        command_runner = AwsCommandRunner(filters)

        for region_name in self.region_names:
            self.init_region_cache(region_name)

            # if thing_name is none, get all things and check
            if self.thing_name is None:
                client = self.session.client("iot", region_name=region_name)
                things = client.list_things()
                thing_options = IotOptions(
                    verbose=verbose,
                    filters=filters,
                    session=self.session,
                    region_name=region_name,
                    thing_name=things,
                )
                diagram_builder: BaseDiagram
                if diagram:
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
                    verbose=verbose,
                    filters=filters,
                    session=self.session,
                    region_name=region_name,
                    thing_name=things,
                )

                if diagram:
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
