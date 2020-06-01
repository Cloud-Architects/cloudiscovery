from shared.command import BaseCommand, CommandRunner
from shared.common import *
from shared.diagram import NoDiagram, BaseDiagram


class ProfileOptions(BaseOptions):
    pass


class Policy(BaseCommand):

    def __init__(self, region_name, session, diagram):
        super().__init__(region_name, session, diagram)

    def run(self):
        self.check_region()

        command_runner = CommandRunner()
        if self.diagram:
            diagram = BaseDiagram("AWS Permissions map", "account_policies")
        else:
            diagram = NoDiagram()
        options = ProfileOptions(session=self.session, region_name=self.region_name)
        command_runner.run("policy", options, diagram)
