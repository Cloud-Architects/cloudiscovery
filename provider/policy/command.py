from shared.command import BaseCommand, CommandRunner
from shared.common import *


class ProfileOptions(BaseOptions):
    pass


class Policy(BaseCommand):

    def __init__(self, region_name, session, diagram):
        super().__init__(region_name, session, diagram)

    def run(self):
        self.check_region()

        command_runner = CommandRunner()
        options = ProfileOptions(session=self.session, region_name=self.region_name)
        command_runner.run("policy", options)
